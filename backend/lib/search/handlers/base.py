import hashlib
from typing import Type, Optional, Any
from typing import Union

import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import ValidationError

from lib.database.connection import Database
from lib.moderation import ModerationResult
from lib.search.search_item import SearchChar, SearchLore


class ElasticItemHandler:
    def __init__(self, data: dict):
        self._node_row = data
        self._def_row = {}

    def fetch_more_data(self):
        # Default is do nothing.
        self._def_row = {}

    def _generate_doc_id(self) -> str:
        raise NotImplementedError()

    def doc_id(self):
        return hashlib.md5(self._generate_doc_id().encode('utf-8')).hexdigest()

    def _do_create_item(self) -> Union[SearchChar, SearchLore, None]:
        raise NotImplementedError()

    def create_item(self) -> Union[SearchChar, SearchLore, None]:
        model = self._do_create_item()
        if not model:
            return None
        try:
            # Manually verify the safety data since some items won't have any safety data yet.
            safety = ModerationResult(**model.safety)
        except ValidationError:
            return None
        model.safety = safety.model_dump()
        return model

    def console_identifier(self):
        raise NotImplementedError()


class ElasticHandler:
    def __init__(
            self,
            name: str,
            table_name: str,
            primary_key: str,
            handler_cls: Type['ElasticItemHandler']
    ):
        self._name = name
        self._table_name = table_name
        self._temp_table_name = f"temp_{table_name}"
        self._primary_key = primary_key
        self._handler_cls = handler_cls
        self._cursor = None
        self._conn = None
        self._last_key: Optional[Any] = None  # Internal tracker for keyset pagination

    @property
    def name(self) -> str:
        return self._name

    @property
    def handler_cls(self):
        return self._handler_cls

    def connect(self):
        self._conn = Database.get_connection()
        self._cursor = self._conn.cursor(cursor_factory=RealDictCursor)

    def close(self):
        if self._cursor:
            self._cursor.close()
        if self._conn:
            self._conn.commit()
            Database.return_connection(self._conn)

    def create_temp_table(self):
        create_temp_table_query = f"""
            CREATE TEMPORARY TABLE {self._temp_table_name} AS 
            SELECT * FROM {self._table_name}
        """
        self._cursor.execute(create_temp_table_query)

        # Create an index on the primary key to optimize ORDER BY and WHERE clauses
        create_index_query = f"""
            CREATE INDEX idx_{self._temp_table_name}_{self._primary_key} 
            ON {self._temp_table_name} ({self._primary_key})
        """
        self._cursor.execute(create_index_query)

    def drop_temp_table(self):
        raise Exception("Don't need to do this, it's automatically removed on connnection closure")
        drop_temp_table_query = f"DROP TABLE IF EXISTS {self._temp_table_name}"
        self._cursor.execute(drop_temp_table_query)

    def count_num_rows(self) -> int:
        query = f"SELECT COUNT(*) FROM {self._temp_table_name}"
        self._cursor.execute(query)
        return self._cursor.fetchone()['count']

    def get_rows_in_batches(self, batch_size: int) -> list[Any]:
        """
        Retrieves the next batch of rows using keyset pagination.

        Args:
            batch_size (int): The number of rows to retrieve in this batch.

        Returns:
            Tuple containing the new last_key and the list of retrieved rows.
            If no more rows are available, returns (None, []).
        """
        if self._last_key is None:
            # Initial fetch: no last_key, retrieve the first batch
            query = f"""
                SELECT * FROM {self._temp_table_name}
                ORDER BY {self._primary_key} ASC
                LIMIT %s
            """
            self._cursor.execute(query, (batch_size,))
        else:
            # Subsequent fetches: retrieve rows where primary_key > last_key
            query = f"""
                SELECT * FROM {self._temp_table_name}
                WHERE {self._primary_key} > %s
                ORDER BY {self._primary_key} ASC
                LIMIT %s
            """
            self._cursor.execute(query, (self._last_key, batch_size))

        rows = self._cursor.fetchall()
        if not rows:
            # No more rows to fetch
            return []

        # Update the last_key to the primary_key of the last row in this batch
        self._last_key = rows[-1][self._primary_key]
        return rows

    def save_summary(self, doc_id: str, summary: str):
        # Check if the id already exists in the table
        check_query = 'SELECT COUNT(*) FROM embedding_summaries WHERE id = %s'
        self._cursor.execute(check_query, (doc_id,))
        count = self._cursor.fetchone()
        if count and count['count'] == 0:
            # Insert only if it doesn't
            insert_query = 'INSERT INTO embedding_summaries(id, summary) VALUES (%s, %s)'
            self._cursor.execute(insert_query, (doc_id, summary))
        self._conn.commit()

    def get_summary(self, doc_id: str) -> Union[str, None]:
        query = 'SELECT * FROM embedding_summaries WHERE id = %s'
        try:
            self._cursor.execute(query, (doc_id,))
            result = self._cursor.fetchone()
            if not result:
                return None
            return result['summary']
        except psycopg2.ProgrammingError:
            return None

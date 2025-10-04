import json
from typing import List

from psycopg2.extras import RealDictCursor

from lib.database.connection import CursorFromConnectionFromPool


class SafetyHandler:
    _FILTER_UNPROCESSED = "WHERE NOT (metadata ? 'safety')"  # OR jsonb_extract_path_text(metadata::jsonb, 'safety', 'categories', 'hate') IS NULL"
    _ITERATE_BATCH_SIZE = 100

    def __init__(self, def_table: str, meta_table: str, def_select_cols: tuple, def_primary_key: str, meta_primary_key: str, name_format: str, tqdm_desc: str, reprocess: bool = False):
        self._def_table = def_table
        self._meta_table = meta_table
        self._def_select_cols = def_select_cols
        self._def_primary_key = def_primary_key
        self._meta_primary_key = meta_primary_key
        self.name_format = name_format
        self.tqdm_desc = tqdm_desc
        self._reprocess = reprocess
        self._iterate_offset = 0

    def _sql_all_cards(self) -> str:
        return f'SELECT * FROM {self._meta_table} WHERE hidden IS NOT true'

    def fetch_all_cards(self) -> List[dict]:
        with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(self._sql_all_cards())
            rows = cursor.fetchall()
        return [dict(r) for r in rows]

    def total_card_rows(self) -> int:
        with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM {self._def_table}" + (' ' + self._FILTER_UNPROCESSED if not self._reprocess else ''))
            total_rows = cursor.fetchone()['count']
        return total_rows

    def iterate_rows(self) -> List[dict]:
        with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
            query = f"SELECT {', '.join(self._def_select_cols)} FROM {self._def_table}"
            conditions = []
            if not self._reprocess:
                conditions.append(self._FILTER_UNPROCESSED.lstrip('WHERE '))
            if self._iterate_offset:
                conditions.append(f"{self._def_primary_key} > '{self._iterate_offset}'")
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += f" ORDER BY {self._def_primary_key} LIMIT {self._ITERATE_BATCH_SIZE}"

            cursor.execute(query)
            rows = cursor.fetchall()
            if rows:
                self._iterate_offset = rows[-1][self._def_primary_key]  # Update offset to the last processed primary key
            return [dict(r) for r in rows]

    def _sql_update_metadata(self) -> str:
        return f'UPDATE {self._def_table} SET metadata = %s WHERE {self._def_primary_key} = %s'

    def _sql_update_metadata_args(self, row: dict) -> tuple:
        return row[self._def_primary_key],

    def _sql_set_hidden(self) -> str:
        return f'UPDATE {self._meta_table} SET hidden = %s WHERE {self._meta_primary_key} = %s'

    def _sql_update_hidden_args(self, row: dict) -> tuple:
        return row[self._meta_primary_key],

    def update_metadata(self, metadata: dict, row: dict):
        with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(self._sql_update_metadata(), (json.dumps(metadata), *self._sql_update_metadata_args(row)))

    def set_hidden(self, row: dict):
        with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(self._sql_set_hidden(), self._sql_update_hidden_args(row))

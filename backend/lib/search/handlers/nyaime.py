import logging

from psycopg2.extras import RealDictCursor

from lib.database.connection import CursorFromConnectionFromPool
from lib.search.search_item import SearchChar
from lib.search.handlers.base import ElasticHandler, ElasticItemHandler
from lib.sources import Sources

logger = logging.getLogger('NyaimeHandler')
logger.setLevel(logging.INFO)


class NyaimeElasticHandler(ElasticHandler):
    def __init__(self):
        super().__init__('Nyaime', 'nyaime_character', 'id', NyaimeElasticItemHandler)


class NyaimeElasticItemHandler(ElasticItemHandler):
    def __init__(self, data: dict):
        super().__init__(data)

    def fetch_more_data(self):
        with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT * FROM nyaime_character_def WHERE id = %s ORDER BY added DESC',
                           (self._node_row['id'],))
            self._def_row = cursor.fetchone()
        if self._def_row is None:
            logger.critical(f'Nyaime character {self._node_row["id"]} has no def!')
            return

    def _generate_doc_id(self) -> str:
        return f'nyaime{self._node_row["author"]}{self._node_row["name"]}{self._node_row["id"]}character'

    def console_identifier(self):
        return f'{self._node_row["author"]}/{self._node_row["name"]} -- {self._node_row["id"]}'

    def _do_create_item(self):
        if not self._node_row or not self._def_row:
            return
        return SearchChar(
            name=self._node_row['name'],
            source=Sources.nyaime.value,
            sourceSpecific=None,
            scenario=self._def_row['definition']['data']['scenario'],
            first_mes=self._def_row['definition']['data']['scenario'],
            description=self._def_row['definition']['data']['description'],
            mes_example=self._def_row['definition']['data']['mes_example'],
            personality=self._def_row['definition']['data']['personality'],
            creator_notes=self._def_row['definition']['data']['creator_notes'],
            system_prompt=self._def_row['definition']['data']['system_prompt'],
            world_scenario=self._def_row['definition']['data']['world_scenario'],
            example_dialogue=self._def_row['definition']['data']['example_dialogue'],
            alternate_greetings=self._def_row['definition']['data']['alternate_greetings'],
            post_history_instructions=self._def_row['definition']['data']['post_history_instructions'],
            created=self._def_row['definition']['create_date'],
            updated=self._node_row['added'],
            added=self._node_row['added'],
            image_hash=self._def_row['image_hash'],
            platform_summary=self._node_row['node']['content'],
            author=self._node_row['author'],
            id=str(self._node_row['id']),
            tagline=self._node_row['node']['tagline'],
            tags=self._def_row['definition']['data']['tags'],
            safety=self._def_row['metadata'].get('safety', {}),
            downloads=self._node_row['node']['downloads'],
            embedding=[],
            token_count=self._def_row['metadata']['totalTokens'],
            doc_id=self.doc_id()
        )

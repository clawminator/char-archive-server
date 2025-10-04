import logging

from psycopg2.extras import RealDictCursor

from lib.database.connection import CursorFromConnectionFromPool
from lib.search.handlers.base import ElasticHandler, ElasticItemHandler
from lib.search.search_item import SearchChar
from lib.sources import Sources

logger = logging.getLogger('CharTavernHandler')
logger.setLevel(logging.INFO)


class CharTavernElasticHandler(ElasticHandler):
    def __init__(self):
        super().__init__('Character Tavern', 'char_tavern_character', 'path', CharTavernElasticItemHandler)


class CharTavernElasticItemHandler(ElasticItemHandler):
    def __init__(self, data: dict):
        super().__init__(data)
        self._path = self._node_row['path']

    def fetch_more_data(self):
        with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT * FROM char_tavern_character_def WHERE PATH = %s ORDER BY added DESC',
                           (self._path,))
            self._def_row = cursor.fetchone()
        if self._def_row is None:
            logger.warning(f'Character Tavern {self._path} has no def!')
            return

    def _generate_doc_id(self) -> str:
        return f'char_tavern{self._node_row["author"]}{self._node_row["path"]}{self._path}character'

    def console_identifier(self):
        return self._path

    def _do_create_item(self):
        if not self._node_row or not self._def_row:
            return

        created_at = None
        if self._def_row['definition'].get('create_date'):
            created_at = self._def_row['definition']['create_date']
        elif self._def_row['definition']['data'].get('creation_date'):
            created_at = self._def_row['definition']['data']['creation_date']
        assert created_at

        return SearchChar(
            name=self._node_row['name'],
            source=Sources.char_tavern.value,
            sourceSpecific=None,
            scenario=self._def_row['definition']['data']['scenario'],
            first_mes=self._def_row['definition']['data']['scenario'],
            description=self._def_row['definition']['data']['description'],
            mes_example=self._def_row['definition']['data']['mes_example'],
            personality=self._def_row['definition']['data']['personality'],
            creator_notes=self._def_row['definition']['data']['creator_notes'],
            system_prompt=self._def_row['definition']['data']['system_prompt'],
            world_scenario=self._def_row['definition']['data'].get('world_scenario', ''),
            example_dialogue=self._def_row['definition']['data']['mes_example'],
            alternate_greetings=self._def_row['definition']['data']['alternate_greetings'],
            post_history_instructions=self._def_row['definition']['data']['post_history_instructions'],
            created=created_at,
            updated=self._node_row['updated'],
            added=self._def_row['added'],
            image_hash=self._def_row['image_hash'],
            platform_summary=self._node_row['data']['pageDescription'],
            author=self._node_row['author'],
            id=self._node_row['path'],
            tagline=self._node_row['data']['tagline'],
            tags=self._node_row['data']['tags'],
            safety=self._def_row['metadata'].get('safety', {}),
            downloads=self._node_row['data']['downloads'],
            embedding=[],
            token_count=self._def_row['metadata']['totalTokens'],
            doc_id=self.doc_id()
        )

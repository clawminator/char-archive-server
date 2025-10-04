import logging
from datetime import datetime

from psycopg2.extras import RealDictCursor

from lib.database.connection import CursorFromConnectionFromPool
from lib.search.handlers.base import ElasticHandler, ElasticItemHandler
from lib.search.search_item import SearchChar
from lib.routes.v1.handlers.risuai import _risuai_tagline_from_desc
from lib.sources import Sources

logger = logging.getLogger('RisuaiHandler')
logger.setLevel(logging.INFO)


class RisuaiElasticHandler(ElasticHandler):
    def __init__(self):
        super().__init__('Risuai', 'risuai_character', 'id', RisuaiElasticItemHandler)


class RisuaiElasticItemHandler(ElasticItemHandler):
    def __init__(self, data: dict):
        super().__init__(data)

    def fetch_more_data(self):
        with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT * FROM risuai_character_def WHERE id = %s ORDER BY added DESC',
                           (self._node_row['id'],))
            self._def_row = cursor.fetchone()
        if self._def_row is None:
            logger.critical(f'Risuai character {self._node_row["id"]} has no def!')
            return

    def _generate_doc_id(self) -> str:
        return f'risuai{self._node_row["author"]}{self._node_row["name"]}{self._node_row["id"]}character'

    def console_identifier(self):
        return f'{self._node_row["author"]}/{self._node_row["name"]} -- {self._node_row["id"]}'

    def _do_create_item(self):
        if not self._node_row or not self._def_row:
            return
        return SearchChar(
            name=self._node_row['name'],
            source=Sources.risuai.value,
            sourceSpecific=None,
            scenario=self._def_row['definition']['data']['scenario'],
            first_mes=self._def_row['definition']['data']['scenario'],
            description=self._def_row['definition']['data']['description'],
            mes_example=self._def_row['definition']['data']['mes_example'],
            personality=self._def_row['definition']['data']['personality'],
            creator_notes=self._def_row['definition']['data']['creator_notes'],
            system_prompt=self._def_row['definition']['data']['system_prompt'],
            world_scenario='',
            example_dialogue=self._def_row['definition']['data']['mes_example'],
            alternate_greetings=self._def_row['definition']['data']['alternate_greetings'],
            post_history_instructions=self._def_row['definition']['data']['post_history_instructions'],
            created=datetime.fromtimestamp(0),  # datetime.datetime.fromtimestamp(card_row['definition']['data']['creation_date']).isoformat(), # TODO: fix when risuai fixes their shit
            updated=self._node_row['updated'],
            added=self._node_row['added'],
            image_hash=self._def_row['image_hash'],
            platform_summary=self._node_row['node']['desc'],
            author=self._node_row['author'],
            id=str(self._node_row['id']),
            tagline=_risuai_tagline_from_desc(self._node_row['node']['desc']),
            tags=self._def_row['definition']['data']['tags'],
            safety=self._def_row['metadata'].get('safety', {}),
            downloads=self._node_row['node']['download'],
            embedding=[],
            token_count=self._def_row['metadata']['totalTokens'],
            doc_id=self.doc_id()
        )

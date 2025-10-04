import logging

from psycopg2.extras import RealDictCursor

from lib.database.connection import CursorFromConnectionFromPool
from lib.search.handlers.base import ElasticHandler, ElasticItemHandler
from lib.search.handlers.chub import ChubSearchNode
from lib.search.search_item import SearchLore
from lib.sources import Sources

logger = logging.getLogger('ChubHandler')
logger.setLevel(logging.INFO)


class ChubLorebookElasticHandler(ElasticHandler):
    def __init__(self):
        super().__init__('Chub Lorebook', 'chub_lorebook', 'id', ChubLorebookElasticItemHandler)


class ChubLorebookElasticItemHandler(ElasticItemHandler):
    def __init__(self, data: dict):
        super().__init__(data)
        self._full_path = self._node_row["data"]["fullPath"]

    def fetch_more_data(self):
        with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT * FROM chub_lorebook_def WHERE id = %s AND full_path = %s ORDER BY added DESC',
                           (self._node_row['id'], self._full_path))
            self._def_row = cursor.fetchone()
        if self._def_row is None:
            logger.warning(f'Chub lorebook {self._full_path} has no def!')
            return

    def _generate_doc_id(self) -> str:
        return f'chub{self._node_row["author"]}{self._node_row["id"]}{self._full_path}lorebook'

    def console_identifier(self):
        return self._full_path

    def _do_create_item(self):
        if not self._node_row or not self._def_row:
            return
        return ChubLoreSearchNode(
            name=self._node_row['name'],
            source=Sources.chub.value,
            sourceSpecific=None,
            lore_content=[x['content'] for x in self._def_row['definition']['entries']],
            created=self._node_row['data']['createdAt'],
            updated=self._node_row['updated'],
            added=self._node_row['added'],
            image_hash=self._def_row['image_hash'],
            platform_summary=self._node_row['data']['description'],
            chub=ChubSearchNode(
                chub_fullPath=self._node_row['data']['fullPath'].split('/'),
                chub_fork=len([x for x in self._node_row['data']['labels'] if x.get('title', '') == 'Forked']) > 0,
            ),
            author=self._node_row['author'],
            id=str(self._node_row['id']),
            tagline=self._node_row['data']['tagline'],
            tags=self._node_row['data']['topics'],
            safety=self._def_row['metadata'].get('safety', {}),
            downloads=self._node_row['data']['starCount'],
            embedding=[],
            token_count=self._def_row['metadata']['totalTokens'],
            doc_id=self.doc_id()
        )


class ChubLoreSearchNode(SearchLore):
    chub: ChubSearchNode

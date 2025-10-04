import logging
import re

from psycopg2.extras import RealDictCursor

from lib.database.connection import CursorFromConnectionFromPool
from lib.search.handlers.base import ElasticHandler, ElasticItemHandler
from lib.search.handlers.chub import ChubSearchNode
from lib.search.search_item import SearchChar
from lib.sources import Sources

logger = logging.getLogger('ChubHandler')
logger.setLevel(logging.INFO)


class ChubCharacterElasticHandler(ElasticHandler):
    def __init__(self):
        super().__init__('Chub Character', 'chub_character', 'id', ChubCharacterElasticItemHandler)


class ChubCharacterElasticItemHandler(ElasticItemHandler):
    def __init__(self, data: dict):
        super().__init__(data)
        self._full_path = self._node_row["data"]["fullPath"]

    def fetch_more_data(self):
        with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT * FROM chub_character_def WHERE id = %s AND full_path = %s ORDER BY added DESC',
                           (self._node_row['id'], self._full_path))
            self._def_row = cursor.fetchone()
        if self._def_row is None:
            logger.warning(f'Chub character {self._full_path} has no def!')
            return

    def _generate_doc_id(self) -> str:
        return f'chub{self._node_row["author"]}{self._node_row["id"]}{self._full_path}character'

    def console_identifier(self):
        return self._full_path

    def _do_create_item(self):
        if not self._node_row or not self._def_row:
            return

        # Chub will leave the original author on anonymous cards in the avatar URL path when an author deletes their account.
        # Extract it and make it searchable.
        avatar_url = self._node_row['data']['avatar_url']
        avatar_url_author = None
        if self._node_row['author'] == 'Anonymous' and avatar_url:  # only if the author is anonymous.
            m = re.match(r'https://avatars.charhub.io/avatars/(.*?)/', avatar_url)
            if m and m.group(1).lower() != 'anonymous':
                avatar_url_author = m.group(1)

        return ChubCharSearchNode(
            name=self._node_row['name'],
            source=Sources.chub.value,
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
            created=self._node_row['data']['createdAt'],
            updated=self._node_row['updated'],
            added=self._node_row['added'],
            image_hash=self._def_row['image_hash'],
            platform_summary=self._node_row['data']['description'],
            chub=ChubSearchNode(
                chub_fullPath=self._node_row['data']['fullPath'].split('/'),
                chub_fork=len([x for x in self._node_row['data']['labels'] if x.get('title', '') == 'Forked']) > 0,
                chub_anonymousAuthor=avatar_url_author
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


class ChubCharSearchNode(SearchChar):
    chub: ChubSearchNode

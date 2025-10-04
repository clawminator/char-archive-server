import json
import zlib
from datetime import timezone
from typing import Dict, Any, Tuple, List

from dateutil.parser import parse
from psycopg2.extras import RealDictCursor

from lib.config import CARD_IMAGE_ROOT_DIR
from lib.database.connection import CursorFromConnectionFromPool
from lib.database.helpers import check_node_hidden
from lib.helpers.args import parse_int_arg
from lib.routes.v1.handlers.handler import Handler
from lib.routes.v1.response_types.user import UserCardItem
from lib.sources import Sources


def check_nyaime_hidden(node_id: str):
    # TODO: see improvements.txt
    return False
    # return check_node_hidden('nyaime_character', 'id', node_id)


def _parse_nyaime_ratings(comments: dict):
    ratings = list(reversed(sorted([{'comment': x['Content'], 'created': parse(x['Date'])} for x in comments], key=lambda x: x['created'])))
    return [{'comment': x['comment'], 'created': x['created'].astimezone(timezone.utc).isoformat()} for x in ratings]


def _get_nyaime_node_versions(node_id: int):
    with CursorFromConnectionFromPool() as cursor:
        cursor.execute(f"SELECT added FROM nyaime_character_def WHERE id = %s", (node_id,))
        result = list(sorted(([x[0] for x in cursor.fetchall()]), reverse=True))

    output = {}
    for i in range(len(result)):
        output[str(i)] = str(result[i].astimezone(timezone.utc).isoformat())

    return output


def _build_nyaime_user(username: str):
    with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
        cursor.execute('SELECT * FROM nyaime_user WHERE name = %s', (username,))
        result = cursor.fetchall()
    if not len(result):
        return None
    result = result[0]

    return {
        'username': ('!' if result['is_guest'] else '') + username,
        'description': result['bio'].strip('"'),
        'id': None,
        'data': {},
        'avatar': {
            'hash': None
        },
        'updated': result['updated'].isoformat(),
        'added': result['added'].isoformat(),
        'characters': _get_nyaime_user_cards(username),
        'lorebooks': [],
        'source': Sources.nyaime.value,
    }


def _get_nyaime_user_cards(username: str):
    with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
        cursor.execute('SELECT * FROM nyaime_character WHERE author = %s', (username,))
        data = [dict(x) for x in cursor.fetchall()]
    result = []
    for card in data:
        card = dict(card)
        result.append(UserCardItem(
            id=card['id'],
            name=card['name'],
            created=parse(card['node']['created']).astimezone(timezone.utc).isoformat(),
            description=card['node']['content'],
            tagline=card['node']['tagline'],
            source=Sources.nyaime.value,
            added=card['added'],
            downloads=card['node']['downloads'],
            type='character'
        ))
    return result


class NyaimeHandler(Handler):
    def __init__(self, parts: list, node_type: str, version: int):
        super().__init__(source=Sources.nyaime, parts=parts, node_type=node_type, version=version)

    def _build_parts(self, parts: list) -> list:
        author, node_id = parts
        if author.startswith('!'):
            author = author[1:]
        node_id_int, _ = parse_int_arg(node_id, '')
        return [author, node_id_int]

    def check_parts(self) -> Tuple[int, str | None]:
        if not self.parts or len(self.parts) != 2:
            return 400, 'invalid item path'
        author, node_id = self.parts
        node_id_int, _ = parse_int_arg(node_id, '')
        if not isinstance(node_id_int, int):
            return 400, 'invalid node ID'
        return 200, None

    def handle_node(self) -> Tuple[dict | None, int, str | None]:
        author, node_id = self.parts
        with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM nyaime_character WHERE author = %s AND id = %s", (author, node_id))
            node_result = cursor.fetchone()
            if node_result is None:
                return None, 404, 'character not found'
            cursor.execute("SELECT * FROM nyaime_character_def WHERE author = %s AND id = %s", (author, node_id))
            def_result = cursor.fetchone()
        selected_card: Dict[str, Any] = dict(node_result)
        selected_card['description'] = selected_card['node']['description']
        selected_card['tagline'] = selected_card['node']['tagline']
        selected_card['added'] = selected_card['added']
        selected_card['updated'] = selected_card['updated']
        selected_card['ratings'] = _parse_nyaime_ratings(selected_card['node']['comments'])
        selected_card['created'] = selected_card['node']['created']
        selected_card['type'] = 'character'
        selected_card['metadata'] = def_result['metadata']
        selected_card['tags'] = selected_card['node']['tags']

        new_node = {
            'author_guest': selected_card['node']['author_guest'],
            'image_url': selected_card['node']['image_url'],
            'downloads': selected_card['node']['downloads'],
            'post_type': selected_card['node']['post_type'],
        }
        selected_card['node'] = new_node

        selected_card['versions'] = _get_nyaime_node_versions(node_id)

        return selected_card, 200, None

    def handle_image(self) -> Tuple[bytes | None, int, str | None]:
        author, node_id = self.parts
        if self.node_type != 'character':
            return None, 400, 'invalid node type'

        with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT image_hash, added FROM nyaime_character_def WHERE author = %s AND id = %s ORDER BY added DESC', (author, node_id,))
            result = [x for x in cursor.fetchall()]
        if not len(result):
            return None, 404, 'character not found'
        if self.version >= len(result):
            return None, 400, 'version not found'

        result = list(sorted([x for x in result], key=lambda d: d['added'], reverse=True))
        hash_str = result[self.version]['image_hash']
        del result

        path = CARD_IMAGE_ROOT_DIR / hash_str[0] / hash_str[1] / hash_str[2] / hash_str[3:]
        if not path.is_file():
            return None, 500, 'file not found'
        return path.read_bytes(), 200, None

    def handle_def(self, original_unmodified: bool) -> Tuple[dict | None, int, str | None]:
        author, node_id = self.parts
        if self.node_type != 'character':
            return None, 400, 'invalid node type'

        with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT definition, raw, added FROM nyaime_character_def WHERE author = %s AND id = %s ORDER BY added DESC', (author, node_id,))
            result = [x for x in cursor.fetchall()]
        if not len(result):
            return None, 404, 'character not found'
        if self.version >= len(result):
            return None, 400, 'version not found'

        result = list(sorted([x for x in result], key=lambda d: d['added'], reverse=True))
        selected_version = result[self.version]
        del result

        if original_unmodified:
            byte_data = selected_version['raw'].tobytes()
            decompressed_data = zlib.decompress(byte_data)
            selected_card = json.loads(decompressed_data.decode())
        else:
            selected_card = selected_version['definition']
        return selected_card, 200, None

    def handle_ratings(self) -> Tuple[List[Dict] | None, int, str | None]:
        author, node_id = self.parts
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('SELECT node FROM nyaime_character WHERE author = %s AND id = %s', (author, node_id,))
            result = cursor.fetchone()
        if result is None:
            return None, 404, 'character not found'
        return _parse_nyaime_ratings(result[0]['comments']), 200, None

    def handle_user(self, username: str) -> dict | None:
        if username.startswith('!'):
            username = username[1:]
        return _build_nyaime_user(username)

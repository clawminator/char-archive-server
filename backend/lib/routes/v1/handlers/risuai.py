import json
import re
import zlib
from datetime import timezone
from typing import Dict, Any, Tuple

from psycopg2.extras import RealDictCursor

from lib.config import CARD_IMAGE_ROOT_DIR
from lib.database.connection import CursorFromConnectionFromPool
from lib.database.helpers import check_node_hidden
from lib.routes.v1.handlers.handler import Handler
from lib.routes.v1.response_types.user import UserCardItem
from lib.sources import Sources


def check_risuai_hidden(node_id: str):
    # TODO: see improvements.txt
    return False
    # return check_node_hidden('risuai_character', 'id', node_id)


def _risuai_tagline_from_desc(desc: str):
    desc_clean = re.sub(r'[.!,"\'?]+$', '', desc.replace('\n', ' ').strip().rstrip('.').rstrip('!'))
    return (desc_clean[:145] + '...') if len(desc_clean) > 75 else desc_clean


def _get_risuai_node_versions(node_id: str):
    with CursorFromConnectionFromPool() as cursor:
        cursor.execute(f"SELECT added FROM risuai_character_def WHERE id = %s", (node_id,))
        result = list(sorted(([x[0] for x in cursor.fetchall()]), reverse=True))

    output = {}
    for i in range(len(result)):
        output[str(i)] = str(result[i].astimezone(timezone.utc).isoformat())

    return output


def _build_risuai_user(username: str):
    with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(f"SELECT * FROM risuai_user WHERE username = %s", (username,))
        user_info = cursor.fetchone()

    return {
        'username': username,
        'id': None,
        'data': {},
        'avatar': {
            'hash': None
        },
        'updated': user_info['updated'],
        'added': user_info['added'],
        'characters': _get_risuai_user_cards(username),
        'lorebooks': [],
        'source': Sources.risuai.value,
        'description': user_info['description'],
    }


def _get_risuai_user_cards(username: str):
    with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
        cursor.execute('SELECT name, node, id FROM risuai_character WHERE author = %s', (username,))
        data = [dict(x) for x in cursor.fetchall()]
    result = []
    for node in data:
        node = dict(node)
        result.append(UserCardItem(
            id=node['id'],
            name=node['name'],
            # 'created': card['created'], # TODO: when risuai fixes their date field
            downloads=node['node']['download'],
            description=node['node']['desc'],
            tagline=_risuai_tagline_from_desc(node['node']['desc']),
            source=Sources.risuai.value,
            type='character'
        ))
    return result


class RisuaiHandler(Handler):
    def __init__(self, parts: list, node_type: str, version: int):
        super().__init__(source=Sources.risuai, parts=parts, node_type=node_type, version=version)

    def check_parts(self) -> Tuple[int, str | None]:
        if not self.parts or len(self.parts) != 2:
            return 400, 'invalid item path'
        return 200, None

    def handle_node(self) -> Tuple[dict | None, int, str | None]:
        author, node_id = self.parts
        with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM risuai_character WHERE author = %s AND id = %s", (author, node_id))
            node_result = cursor.fetchone()
        if node_result is None:
            return None, 404, f'{self.node_type} not found'
        with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT * FROM risuai_character_def WHERE author = %s AND id = %s ORDER BY added DESC', (author, node_id,))
            def_result = cursor.fetchone()
        if not len(def_result):
            return None, 404, f'{self.node_type} not found'

        selected_card: Dict[str, Any] = dict(node_result)
        selected_card['description'] = selected_card['node']['desc']
        selected_card['tagline'] = _risuai_tagline_from_desc(selected_card['node']['desc'])
        selected_card['type'] = 'character'
        selected_card['tags'] = selected_card['node']['tags']
        selected_card['metadata'] = def_result['metadata']
        selected_card['node'] = {
            'downloads': selected_card['node']['download'],
        }
        selected_card['versions'] = _get_risuai_node_versions(node_id)

        return selected_card, 200, None

    def handle_image(self) -> Tuple[bytes | None, int, str | None]:
        author, node_id = self.parts
        with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT image_hash, added FROM risuai_character_def WHERE author = %s AND id = %s ORDER BY added DESC', (author, node_id,))
            result = [dict(x) for x in cursor.fetchall()]
        if not len(result):
            return None, 404, f'{self.node_type} not found'
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
        if self.node_type == 'character':
            with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
                cursor.execute('SELECT definition, raw, added FROM risuai_character_def WHERE author = %s AND id = %s ORDER BY added DESC', (author, node_id,))
                result = [x for x in cursor.fetchall()]
            if not len(result):
                return None, 404, f'{self.node_type} not found'
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
        else:
            return None, 400, 'invalid node type'

    def handle_user(self, username: str) -> dict | None:
        user_data = _build_risuai_user(username)
        if user_data is None:
            return None
        # TODO: after risuai fixes their shit
        # if len(user_data['characters']):
        #     user_data['added'] = list(sorted(user_data['characters'], key=lambda c: parse(c.created)))[0].created
        # else:
        #     user_data['added'] = datetime.datetime.fromtimestamp(0).astimezone(datetime.timezone.utc).isoformat()
        return user_data

import io
import json
import zlib
from datetime import timezone, datetime
from typing import Tuple, List, Dict

from PIL import Image
from psycopg2.extras import RealDictCursor

from lib.config import CARD_IMAGE_ROOT_DIR
from lib.database.connection import CursorFromConnectionFromPool
from lib.helpers.args import double_decode_url_param
from lib.routes.v1.handlers.handler import Handler
from lib.routes.v1.response_types.user import UserCardItem
from lib.sources import Sources


def _get_node_versions(full_path):
    with CursorFromConnectionFromPool() as cursor:
        cursor.execute(f"SELECT added FROM char_tavern_character_def WHERE path = %s", (full_path,))
        result = list(sorted(([x[0] for x in cursor.fetchall()]), reverse=True))

    output = {}
    for i in range(len(result)):
        output[str(i)] = result[i].astimezone(timezone.utc).isoformat()

    return output


def _load_node_data(full_path: str):
    with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(f"SELECT * FROM char_tavern_character WHERE path = %s", (full_path,))
        result = cursor.fetchone()
    if result is None:
        return None, 404, f'character not found'

    result: dict = dict(result)
    versions = _get_node_versions(full_path)

    result['node'] = result.pop('data')
    result['id'] = full_path
    result['node']['createdAt'] = datetime.fromtimestamp(result['node']['createdAt']).isoformat()
    result['created'] = result['node']['createdAt']
    result['node']['lastUpdateAt'] = datetime.fromtimestamp(result['node']['lastUpdateAt']).isoformat()
    result['added'] = versions['0']
    result['type'] = 'character'
    result['tagline'] = result['node']['tagline']
    result['description'] = result['node']['pageDescription'] or ''
    result['node']['path'] = result['node']['path'].split('/')
    result['versions'] = versions
    result['source'] = Sources.char_tavern.value
    result['tags'] = result['node']['tags']

    # Need to change some fields to match the correct format.
    result['ratings'] = []
    for rating in result['reviews']:
        result['ratings'].append({'created': rating['createdAt'], 'comment': rating['comment']})

    with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(f'SELECT * FROM char_tavern_character_def WHERE path = %s ORDER BY added DESC LIMIT 1', (full_path,))
        def_result = cursor.fetchone()
    result['metadata'] = def_result['metadata']

    return result, 200, None


def _get_user(username: str) -> dict:
    with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
        cursor.execute('SELECT * FROM char_tavern_user WHERE username = %s', (username,))
        result = cursor.fetchone()
    if result is None:
        return {
            'username': username,
            'id': None,
            'data': {},
            'avatar': {
                'hash': None,
            },
            'updated': None,
            'added': None,
            'source': Sources.char_tavern.value,
            'missing': True,
            'description': None
        }
    else:
        return dict(result)


def _get_user_cards(user: str):
    with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
        cursor.execute('SELECT * FROM char_tavern_character WHERE author = %s', (user,))
        data: list = [dict(x) for x in cursor.fetchall()]
    result = []
    for card in data:
        with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(f'SELECT * FROM char_tavern_character_def WHERE path = %s ORDER BY added DESC LIMIT 1', (card['path'],))
            def_result = cursor.fetchone()
        result.append(UserCardItem(
            id=card['path'],
            name=card['name'],
            created=datetime.fromtimestamp(card['data']['createdAt']),
            updated=datetime.fromtimestamp(card['data']['lastUpdateAt']),
            downloads=card['data']['downloads'],
            tags=card['data']['tags'],
            description=card['data']['pageDescription'],
            tagline=card['data']['tagline'],
            path=card['path'].split('/'),
            source=Sources.char_tavern.value,
            added=def_result['added'],
            type='character'
        ))
    return result


class CharTavernHandler(Handler):
    def __init__(self, parts: list, node_type: str, version: int):
        super().__init__(source=Sources.char_tavern, parts=parts, node_type=node_type, version=version)

    def _build_parts(self, parts):
        author, char_fullpath = parts
        author = double_decode_url_param(author)
        full_path = f'{author}/{char_fullpath}'
        return [author, full_path]

    def check_parts(self) -> Tuple[int, str | None]:
        if not self.parts or len(self.parts) != 2:
            return 400, 'invalid item path'
        return 200, None

    def handle_node(self) -> Tuple[dict | None, int, str | None]:
        author, full_path = self.parts
        result, code, err = _load_node_data(full_path)
        return result, code, err

    def handle_image(self) -> Tuple[bytes | None, int, str | None]:
        author, full_path = self.parts
        with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(f'SELECT image_hash, added FROM char_tavern_character_def WHERE path = %s ORDER BY added DESC', (full_path,))
            result = [dict(x) for x in cursor.fetchall()]
        if not len(result):
            return None, 404, f'{self.node_type} not found'
        if self.version >= len(result):
            return None, 400, 'version not found'

        result = list(sorted([x for x in result], key=lambda d: d['added'], reverse=True))
        selected_version = result[self.version]

        hash_str = selected_version['image_hash']
        path = CARD_IMAGE_ROOT_DIR / hash_str[0] / hash_str[1] / hash_str[2] / hash_str[3:]
        if not path.is_file():
            return None, 500, 'file not found'
        return path.read_bytes(), 200, None

    def handle_def(self, original_unmodified: bool) -> Tuple[dict | None, int, str | None]:
        author, full_path = self.parts
        with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(f"SELECT definition, raw, added FROM char_tavern_character_def WHERE path = %s ORDER BY added DESC", (full_path,))
            result = [x for x in cursor.fetchall()]
        if not len(result):
            return None, 404, f'{self.node_type} not found'
        if self.version >= len(result):
            return None, 400, 'version not found'

        result = list(sorted([x for x in result], key=lambda d: d['added'], reverse=True))
        selected_version = result[self.version]

        if original_unmodified:
            byte_data = selected_version['raw'].tobytes()
            decompressed_data = zlib.decompress(byte_data)
            selected_card = json.loads(decompressed_data.decode())
        else:
            selected_card = selected_version['definition']
        return selected_card, 200, None

    def handle_ratings(self) -> Tuple[List[Dict] | None, int, str | None]:
        author, full_path = self.parts
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute(f"SELECT reviews FROM char_tavern_character WHERE path = %s", (full_path,))
            result = cursor.fetchone()
        if result is None:
            return None, 404, 'item not found'
        return result, 200, None

    def handle_user(self, username: str) -> dict | None:
        user_data = _get_user(username)
        if user_data is None:
            return None
        if not user_data.get('missing'):
            user_data['description'] = user_data['bio']
            img_path = CARD_IMAGE_ROOT_DIR / user_data['image_hash'][0] / user_data['image_hash'][1] / user_data['image_hash'][2] / user_data['image_hash'][3:]
            user_data['avatar'] = {}
            if not img_path.is_file():
                user_data['avatar']['error'] = 'file not found'
                user_data['avatar']['width'] = None
                user_data['avatar']['height'] = None
            else:
                img = Image.open(io.BytesIO(img_path.read_bytes()))
                user_data['avatar'] = {
                    'width': img.width,
                    'height': img.height,
                }
                del img
            user_data['avatar']['hash'] = user_data.pop('image_hash')
        user_data['characters'] = _get_user_cards(username)
        user_data['source'] = Sources.char_tavern.value
        user_data['description'] = user_data['bio'] or ''
        return user_data

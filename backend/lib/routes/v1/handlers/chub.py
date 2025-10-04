import io
import json
import re
import zlib
from datetime import timezone
from typing import Tuple, List, Dict

from PIL import Image
from dateutil.parser import parse
from psycopg2.extras import RealDictCursor

from lib.config import CARD_IMAGE_ROOT_DIR
from lib.database.connection import CursorFromConnectionFromPool
from lib.helpers.args import double_decode_url_param
from lib.routes.v1.handlers.handler import Handler
from lib.routes.v1.response_types.user import UserCardItem
from lib.sources import Sources


def check_chub_hidden(node_id: str):
    # TODO: see improvements.txt
    return False
    # return check_node_hidden('chub_character', 'id', node_id)


def _get_chub_node_versions(node_type, full_path):
    if node_type not in ['character', 'lorebook']:
        raise Exception

    with CursorFromConnectionFromPool() as cursor:
        cursor.execute(f"SELECT added FROM chub_{node_type}_def WHERE full_path = %s", (full_path,))
        result = list(sorted(([x[0] for x in cursor.fetchall()]), reverse=True))

    output = {}
    for i in range(len(result)):
        output[str(i)] = result[i].astimezone(timezone.utc).isoformat()

    return output, None


def _parse_chub_ratings(ratings: dict):
    return list(reversed(sorted([{'rating': x['rating'], 'comment': x['comment'], 'created': parse(x['created_at']).astimezone(timezone.utc).isoformat()} for x in ratings], key=lambda x: x['created'])))


def _load_node_data(node_type: str, author: str, full_path: str):
    with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(f"SELECT * FROM chub_{node_type} WHERE author = %s AND data->>'fullPath' = %s", (author, full_path))
        result = cursor.fetchone()
    if result is None:
        return None, 404, f'{node_type} not found'

    result['node'] = result.pop('data')
    result['node']['createdAt'] = parse(result['node']['createdAt']).astimezone(timezone.utc).isoformat()
    result['node']['lastActivityAt'] = parse(result['node']['lastActivityAt']).astimezone(timezone.utc).isoformat()
    result['updated'] = result['updated'].astimezone(timezone.utc).isoformat()
    result['added'] = result['added'].astimezone(timezone.utc).isoformat()
    result['type'] = node_type
    result['chub'] = {}

    # Forks
    f = [x for x in result['node']['labels'] if x.get('title', '') == 'Forked']
    if len(f) > 1:
        result['chub']['forked'] = {
            'forked': True,
            'error': 'multiple forks found'
        }
    elif len(f) == 1:
        s = f[0]['description'].split('/')
        if s[0] == 'lorebooks':
            del s[0]
        result['chub']['forked'] = {
            'forked': True,
            'source': s
        }

    if len(result['node']['forks']):
        items = []
        for node_id in result['node']['forks']:
            with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(f"SELECT data FROM chub_{node_type} WHERE id = %s", (node_id,))
                r = cursor.fetchone()
                if r:
                    items.append(r['data']['fullPath'].split('/'))
        result['chub']['forks'] = {
            'count': len(result['node']['forks']),
            'forks': items
        }

    # Sort chats and ratings
    if result.get('chats'):
        result['chats'] = sorted(
            [
                {
                    'count': x['chat_count'],
                    'created': parse(x['created_at']).astimezone(timezone.utc).isoformat()
                    if x['created_at'] else None
                }
                for x in result['chats']['chats']
            ],
            key=lambda x: x['created'] or '',  # Use empty string for None values
            reverse=True
        )

    if result.get('ratings'):
        result['ratings'] = sorted(
            [
                {
                    'rating': x['rating'],
                    'comment': x['comment'],
                    'created': parse(x['created_at']).astimezone(timezone.utc).isoformat()
                    if x['created_at'] else None
                }
                for x in result['ratings']['ratings']
            ],
            key=lambda x: x['created'] or '',  # Use empty string for None values
            reverse=True
        )

    result['tagline'] = result['node']['tagline']
    result['description'] = result['node']['description']

    result['node']['fullPath'] = result['node']['fullPath'].split('/')
    if node_type == 'lorebook':
        del result['node']['fullPath'][0]

    with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(f'SELECT * FROM chub_{node_type}_def WHERE author = %s AND full_path = %s ORDER BY added DESC LIMIT 1', (author, full_path))
        def_result = cursor.fetchone()
    result['metadata'] = def_result['metadata']

    # TODO: make sure the other routes have this
    if node_type == 'character':
        result['creatorNotes'] = def_result['definition']['data']['creator_notes']

    # Same as in the `chub_character.py` search handler.
    avatar_url = result['node']['avatar_url']
    if author == 'Anonymous' and avatar_url:
        m = re.match(r'https://avatars.charhub.io/avatars/(.*?)/', avatar_url)
        if m and m.group(1).lower() != 'anonymous':
            result['chub']['anonymousAuthor'] = m.group(1)

    versions, err = _get_chub_node_versions(node_type, full_path)

    if err:
        return None, 400, err
    result['versions'] = versions

    return result, 200, None


def _get_chub_user(username: str) -> dict:
    with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
        cursor.execute('SELECT * FROM chub_user WHERE username = %s', (username,))
        result = cursor.fetchone()
    if result is None:
        result = {
            'username': username,
            'id': None,
            'data': {},
            'avatar': {
                'hash': None,
            },
            'updated': None,
            'added': None,
            'source': Sources.chub.value,
            'missing': True,
            'description': ''
        }
    return result


def _get_chub_user_cards(user: str):
    with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
        cursor.execute('SELECT * FROM chub_character WHERE author = %s', (user,))
        data: list = [dict(x) for x in cursor.fetchall()]
    result = []
    for card in data:
        result.append(UserCardItem(
            id=card['id'],
            name=card['name'],
            created=card['data']['createdAt'],
            updated=card['data']['lastActivityAt'],
            downloads=card['data']['starCount'],
            tags=card['data']['topics'],
            description=card['data']['description'],
            tagline=card['data']['tagline'],
            path=card['data']['fullPath'].split('/'),
            source=card['source'],
            added=card['added'],
            type='character'
        ))
    return result


def _get_chub_user_lorebooks(user: str):
    with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
        cursor.execute('SELECT * FROM chub_lorebook WHERE author = %s', (user,))
        data: list = [dict(x) for x in cursor.fetchall()]
    result = []
    for card in data:
        result.append(UserCardItem(
            id=card['id'],
            name=card['name'],
            created=card['data']['createdAt'],
            updated=card['data']['lastActivityAt'],
            downloads=card['data']['starCount'],
            tags=card['data']['topics'],
            description=card['data']['description'],
            tagline=card['data']['tagline'],
            path=card['data']['fullPath'].split('/'),
            added=card['added'],
            source=card['source'],
            type='lorebook'
        ))
    return result


class ChubHandler(Handler):
    def __init__(self, parts: list, node_type: str, version: int):
        super().__init__(source=Sources.chub, parts=parts, node_type=node_type, version=version)

    def _build_parts(self, parts):
        author, char_fullpath = parts
        author = double_decode_url_param(author)
        full_path = f'{author}/{char_fullpath}'
        if self.node_type == 'lorebook':
            full_path = 'lorebooks/' + full_path
        return [author, full_path]

    def check_parts(self) -> Tuple[int, str | None]:
        if not self.parts or len(self.parts) != 2:
            return 400, 'invalid item path'
        return 200, None

    def handle_node(self) -> Tuple[dict | None, int, str | None]:
        author, full_path = self.parts
        if self.node_type not in ['character', 'lorebook']:
            return None, 400, 'invalid node type'
        else:
            result, code, err = _load_node_data(self.node_type, author, full_path)
            return result, code, err

    def handle_image(self) -> Tuple[bytes | None, int, str | None]:
        author, full_path = self.parts
        with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(f'SELECT image_hash, added FROM chub_{self.node_type}_def WHERE author = %s AND full_path = %s ORDER BY added DESC', (author, full_path))
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
            cursor.execute(f"SELECT definition, raw, added FROM chub_{self.node_type}_def WHERE author = %s AND full_path = %s ORDER BY added DESC", (author, full_path,))
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
            cursor.execute(f"SELECT ratings FROM chub_{self.node_type} WHERE author = %s AND data->>'fullPath' = %s", (author, full_path))
            result = cursor.fetchone()
        if result is None:
            return None, 404, 'item not found'
        return _parse_chub_ratings(result[0]['ratings']), 200, None

    def handle_chats(self) -> Tuple[List[Dict] | None, int, str | None]:
        author, full_path = self.parts
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("SELECT chats FROM chub_character WHERE data->>'fullPath' = %s", (full_path,))
            result = cursor.fetchone()
        if result is None:
            return None, 400, 'item not found'
        return result[0].get('chats', []), 200, None

    def handle_user(self, username: str) -> dict | None:
        user_data = _get_chub_user(username)
        if user_data is None:
            return None
        if not user_data.get('missing'):
            user_data['description'] = user_data['data']['bio']
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
        user_data['characters'] = _get_chub_user_cards(username)
        user_data['lorebooks'] = _get_chub_user_lorebooks(username)
        return user_data

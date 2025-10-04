import datetime
import json
import zlib
from datetime import timezone
from typing import Dict, Any, Tuple, List

from dateutil.parser import parse
from psycopg2.extras import RealDictCursor

from lib.config import CARD_IMAGE_ROOT_DIR
from lib.database.connection import CursorFromConnectionFromPool
from lib.database.helpers import check_node_hidden
from lib.routes.v1.handlers.handler import Handler
from lib.routes.v1.response_types.user import UserCardItem
from lib.sources import Sources


def check_booru_hidden(node_id: str):
    # TODO: see improvements.txt
    return False
    # return check_node_hidden('booru_character_def', 'id', node_id)


def _get_booru_user_cards(username: str):
    with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
        cursor.execute('SELECT * FROM booru_character_def WHERE author = %s', (username,))
        data = [dict(x) for x in cursor.fetchall()]
    result = []
    for card in data:
        card = dict(card)
        result.append({
            'id': card['id'],
            'name': card['name'],
            'created': card['created'],
            'description': card['summary'],
            'tagline': card['tagline'],
            'source': 'booru',
            'added': card['added']
        })
    return [UserCardItem(**x) for x in result]


def _parse_booru_ratings(comments: dict):
    return list(reversed(sorted([{'comment': x['text'], 'created': x['date']} for x in comments], key=lambda x: x['created'])))


def _build_booru_user(username: str):
    return {
        'username': username,
        'id': '',
        'data': {},
        'avatar': {
            'hash': ''
        },
        'updated': datetime.datetime.fromtimestamp(0).isoformat(),
        'added': datetime.datetime.fromtimestamp(0).isoformat(),
        'characters': _get_booru_user_cards(username),
        'lorebooks': [],
        'source': Sources.booru.value,
    }


def _get_booru_user_cards(username: str):
    with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
        cursor.execute('SELECT * FROM booru_character_def WHERE author = %s', (username,))
        data = [dict(x) for x in cursor.fetchall()]
    result = []
    for card in data:
        card = dict(card)
        result.append(UserCardItem(
            id=card['id'],
            name=card['name'],
            created=card['created'],
            description=card['summary'],
            tagline=card['tagline'],
            source=Sources.booru.value,
            added=card['added'],
            type='character'
        ))
    return result


class BooruHandler(Handler):
    def __init__(self, parts: list, node_type: str, version: int):
        super().__init__(source=Sources.booru, parts=parts, node_type=node_type, version=version)

    def check_parts(self) -> Tuple[int, str | None]:
        if not self.parts or len(self.parts) != 1:
            return 400, 'invalid item path'
        return 200, None

    def handle_node(self) -> Tuple[dict | None, int, str | None]:
        node_id = self.parts[0]
        with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM booru_character_def WHERE id = %s", (node_id,))
            result = cursor.fetchone()
        if result is None:
            return None, 404, 'character not found'
        selected_card: Dict[str, Any] = dict(result)
        selected_card['description'] = selected_card.pop('summary')
        selected_card['tagline'] = selected_card.pop('tagline')
        selected_card['id'] = node_id
        selected_card['created'] = selected_card['created'].astimezone(timezone.utc).isoformat()
        selected_card['added'] = selected_card['added'].astimezone(timezone.utc).isoformat()
        selected_card['ratings'] = _parse_booru_ratings(selected_card.pop('comments'))
        selected_card['metadata']['created'] = parse(selected_card['created']).astimezone(timezone.utc).isoformat()
        selected_card['creatorNotes'] = selected_card['definition']['data']['creator_notes']
        selected_card['type'] = 'character'
        selected_card['tags'] = result['tags']
        return selected_card, 200, None

    def handle_image(self) -> Tuple[bytes | None, int, str | None]:
        node_id = self.parts[0]
        with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT image_hash FROM booru_character_def WHERE id = %s', (node_id,))
            result = cursor.fetchone()
        if result is None:
            return None, 404, 'character not found'
        hash_str = result['image_hash']
        path = CARD_IMAGE_ROOT_DIR / hash_str[0] / hash_str[1] / hash_str[2] / hash_str[3:]
        if not path.is_file():
            return None, 500, 'file not found'
        return path.read_bytes(), 200, None

    def handle_def(self, original_unmodified: bool) -> Tuple[dict | None, int, str | None]:
        node_id = self.parts[0]
        with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT definition, raw FROM booru_character_def WHERE id = %s", (node_id,))
            result = cursor.fetchone()
        if result is None:
            return None, 404, 'character not found'
        if original_unmodified:
            byte_data = result['raw'].tobytes()
            decompressed_data = zlib.decompress(byte_data)
            selected_card = json.loads(decompressed_data.decode())
        else:
            selected_card = result['definition']
        return selected_card, 200, None

    def handle_ratings(self) -> Tuple[List[Dict] | None, int, str | None]:
        node_id = self.parts[0]
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("SELECT comments FROM booru_character_def WHERE id = %s", (node_id,))
            result = cursor.fetchone()
        if result is None:
            return None, 404, 'character not found'
        return _parse_booru_ratings(result[0]), 200, None

    def handle_user(self, username: str) -> dict | None:
        user_data = _build_booru_user(username)
        if user_data is None:
            return None
        if len(user_data['characters']):
            user_data['added'] = list(sorted(user_data['characters'], key=lambda c: parse(c.created)))[0].created
        else:
            user_data['added'] = datetime.datetime.fromtimestamp(0).astimezone(datetime.timezone.utc).isoformat()
        return user_data

import datetime
import json
import zlib
from datetime import timezone
from typing import Dict, Any, Tuple

from dateutil.parser import parse
from psycopg2.extras import RealDictCursor

from lib.config import CARD_IMAGE_ROOT_DIR
from lib.database.connection import CursorFromConnectionFromPool
from lib.database.helpers import check_node_hidden
from lib.helpers.string import make_not_null
from lib.routes.v1.handlers.generic import build_generic_user_cards
from lib.routes.v1.handlers.handler import Handler
from lib.sources import Sources


def check_webring_hidden(node_id: str):
    # TODO: see improvements.txt
    return False
    # return check_node_hidden('webring_character_def', 'card_data_hash', node_id)


def _get_webring_user_cards(username: str):
    with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
        cursor.execute('SELECT * FROM webring_character_def WHERE author = %s', (username,))
        data = [dict(x) for x in cursor.fetchall()]
    return build_generic_user_cards(data, source='webring', source_specific_key=None)


def _build_webring_user(username: str):
    characters = _get_webring_user_cards(username)
    return {
        'username': username,
        'id': '',
        'data': {},
        'avatar': {
            'hash': ''
        },
        'updated': max(characters, key=lambda x: x.added).updated if len(characters) else datetime.datetime.fromtimestamp(0).isoformat(),
        'added': min(characters, key=lambda x: x.added).added if len(characters) else datetime.datetime.fromtimestamp(0).isoformat(),
        'characters': characters,
        'lorebooks': [],
        'source': Sources.webring.value,
    }


# def _get_webring_user_cards(username: str):
#     with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
#         cursor.execute('SELECT * FROM webring_character_def WHERE author = %s', (username,))
#         data = [dict(x) for x in cursor.fetchall()]
#     result = []
#     for card in data:
#         card = dict(card)
#         ccv2_create_date = card['definition'].get('create_date')
#         ccv3_create_date = card['definition']['data'].get('creation_date')
#         if ccv3_create_date:
#             create_date = ccv3_create_date
#         else:
#             create_date = ccv2_create_date
#
#         result.append(UserCardItem(
#             id=card['card_data_hash'],
#             name=card['name'],
#             created=create_date,
#             description=None,
#             tagline=card['tagline'],
#             source=Sources.webring.value,
#             added=card['added'],
#             type='character'
#         ))
#     return result


class WebringHandler(Handler):
    def __init__(self, parts: list, node_type: str, version: int):
        super().__init__(source=Sources.webring, parts=parts, node_type=node_type, version=version)

    def check_parts(self) -> Tuple[int, str | None]:
        if not self.parts or len(self.parts) != 1:
            return 400, 'invalid item path'
        return 200, None

    def handle_node(self) -> Tuple[dict | None, int, str | None]:
        node_id = self.parts[0]
        with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM webring_character_def WHERE card_data_hash = %s", (node_id,))
            result = cursor.fetchone()
        if result is None:
            return None, 404, 'character not found'
        selected_card: Dict[str, Any] = dict(result)
        selected_card['description'] = make_not_null(selected_card.pop('summary'))
        selected_card['tagline'] = selected_card.pop('tagline')
        selected_card['id'] = node_id
        selected_card['created'] = None
        selected_card['added'] = selected_card['added'].astimezone(timezone.utc).isoformat()
        selected_card['ratings'] = []
        selected_card['creatorNotes'] = selected_card['definition']['data']['creator_notes']
        selected_card['type'] = 'character'
        selected_card['tags'] = selected_card['definition']['data']['tags']
        selected_card['author'] = selected_card['author']
        return selected_card, 200, None

    def handle_image(self) -> Tuple[bytes | None, int, str | None]:
        node_id = self.parts[0]
        with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT image_hash FROM webring_character_def WHERE card_data_hash = %s', (node_id,))
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
            cursor.execute("SELECT definition, raw FROM webring_character_def WHERE card_data_hash = %s", (node_id,))
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

    def handle_user(self, username: str) -> dict | None:
        user_data = _build_webring_user(username)
        if user_data is None:
            return None
        if len(user_data['characters']):
            user_data['added'] = list(sorted(user_data['characters'], key=lambda c: parse(c.created)))[0].created
        else:
            user_data['added'] = datetime.datetime.fromtimestamp(0).astimezone(datetime.timezone.utc).isoformat()
        return user_data

import json
import zlib
from datetime import datetime
from typing import Tuple, Any, List, Union

from psycopg2.extras import RealDictCursor

from lib.config import CARD_IMAGE_ROOT_DIR
from lib.database.connection import CursorFromConnectionFromPool
from lib.helpers.string import make_not_null
from lib.routes.v1.handlers.handler import Handler
from lib.routes.v1.response_types.user import UserCardItem
from lib.sources import Sources


def check_generic_hidden(node_id: str) -> bool:
    # TODO: see improvements.txt
    return False
    # return check_node_hidden('generic_character_def', 'card_data_hash', node_id)


def _build_generic_user(username: str):
    return {
        'username': username,
        'id': '',
        'data': {},
        'avatar': {
            'hash': ''
        },
        'updated': datetime.fromtimestamp(0).isoformat(),
        'added': datetime.fromtimestamp(0).isoformat(),
        'characters': _get_generic_user_cards(username),
        'lorebooks': [],
        'source': Sources.generic.value,
    }


def build_generic_user_cards(data: List[Any], source: str, source_specific_key: Union[str, None]) -> List[UserCardItem]:
    """
    Converts a list of card data dictionaries into a list of UserCardItem objects.
    Used by the Generic and Webring handlers.
    """
    result = []
    for card in data:
        card = dict(card)
        create_date = None

        if 'definition' in card:
            definition = card['definition']
            if isinstance(definition, dict):
                create_date = definition.get('creation_date') or definition.get('create_date')
        if not create_date and 'data' in card:
            data_field = card['data']
            if isinstance(data_field, dict):
                create_date = data_field.get('creation_date')
        assert create_date is not None

        user_card_item = UserCardItem(
            id=card.get('card_data_hash'),
            name=card.get('name'),
            description=card.get('summary'),
            tagline=card.get('tagline'),
            source=source,
            sourceSpecific=card[source_specific_key] if source_specific_key else None,
            created=create_date,
            added=card.get('added'),
            type='character'
        )
        result.append(user_card_item)

    return result


def _get_generic_user_cards(username: str):
    with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM generic_character_def WHERE definition->'data'->>'creator' = %s", (username,))
        data = [dict(x) for x in cursor.fetchall()]
    return build_generic_user_cards(data, source='generic', source_specific_key='source')


class GenericHandler(Handler):
    def __init__(self, parts: list, node_type: str, version: int):
        super().__init__(source=Sources.generic, parts=parts, node_type=node_type, version=version)

    def check_parts(self) -> Tuple[int, str | None]:
        if not self.parts or len(self.parts) != 1:
            return 400, 'invalid item path'
        return 200, None

    def handle_node(self) -> Tuple[dict | None, int, str | None]:
        data_hash = self.parts[0]
        if self.node_type == 'character':
            with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM generic_character_def WHERE card_data_hash = %s", (data_hash,))
                result = cursor.fetchone()
            if result is None:
                return None, 404, 'character not found'
            selected_card = dict(result)
            selected_card['id'] = selected_card.pop('card_data_hash')
            selected_card['tagline'] = make_not_null(selected_card['tagline'])
            selected_card['description'] = make_not_null(selected_card.pop('summary'))
            selected_card['sourceSpecific'] = selected_card['source']
            selected_card['source'] = 'generic'
            selected_card['creatorNotes'] = selected_card['definition']['data']['creator_notes']
            selected_card['type'] = self.node_type
            selected_card['author'] = selected_card['definition']['data']['creator']
            selected_card['metadata']['source_url'] = selected_card.pop('source_url')
            selected_card['tags'] = selected_card['definition']['data']['tags']
            selected_card['updated'] = None
            if selected_card['metadata'].get('created'):
                selected_card['created'] = selected_card['metadata'].pop('created')
            return selected_card, 200, None
        else:
            return None, 400, 'invalid node type'

    def handle_image(self) -> Tuple[bytes | None, int, str | None]:
        card_data_hash = self.parts[0]
        if self.node_type == 'character':
            with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
                cursor.execute('SELECT image_hash FROM generic_character_def WHERE card_data_hash = %s', (card_data_hash,))
                result = cursor.fetchone()
            if result is None:
                return None, 404, 'character not found'
            result = dict(result)
            hash_str = result['image_hash']
            path = CARD_IMAGE_ROOT_DIR / hash_str[0] / hash_str[1] / hash_str[2] / hash_str[3:]
            if not path.is_file():
                return None, 500, 'file not found'
            return path.read_bytes(), 200, None
        else:
            return None, 400, 'invalid node type'

    def handle_def(self, original_unmodified: bool) -> Tuple[dict | None, int, str | None]:
        card_data_hash = self.parts[0]
        if self.node_type == 'character':
            with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT definition, raw FROM generic_character_def WHERE card_data_hash = %s", (card_data_hash,))
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
        else:
            return None, 400, 'invalid node type'

    def handle_user(self, username: str) -> dict | None:
        return _build_generic_user(username)

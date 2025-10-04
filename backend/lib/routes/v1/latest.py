import logging
import traceback

from dateutil.parser import parse
from flask import jsonify, request
from psycopg2.extras import RealDictCursor

from . import bp1
from .response_types.error import ErrorResponse
from .response_types.random_latest import ChubRandomOrLatestResponseItem, GenericRandomOrLatestResponseItem, BooruRandomOrLatestResponseItem, NyaimeRandomOrLatestResponseItem, RisuaiRandomOrLatestResponseItem, WebringRandomOrLatestResponseItem, CharTavernRandomOrLatestResponseItem
from ...config import GLOBAL_CACHE_SECONDS
from ...database.connection import CursorFromConnectionFromPool
from ...flask import limiter, cache, get_remote_address_proxied
from ...helpers.args import parse_int_arg
from ...sources import Sources

_logger = logging.getLogger('SERVER').getChild('LATEST')


# REMINDER: if shit is missing from the latest list, it's because the safety daemon hasn't scanned it yet.


def _parse_query(query_result, source: Sources):
    output = []
    for i, _ in enumerate(query_result):
        card_data: dict = dict(query_result[i])
        if source == Sources.chub:
            with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(f'SELECT * FROM chub_character WHERE author = %s AND id = %s', (card_data['author'], card_data['id']))
                node_result = cursor.fetchone()
                if node_result is None:
                    continue
            card_data['fullPath'] = card_data['full_path'].split('/')
            node_result['fullPath'] = node_result['data']['fullPath'].split('/')
            result = ChubRandomOrLatestResponseItem(**{**node_result['data'], **node_result, **card_data}, chub=node_result)
        elif source == Sources.booru:
            result = BooruRandomOrLatestResponseItem(**card_data)
        elif source == Sources.nyaime:
            result = NyaimeRandomOrLatestResponseItem(**card_data)
        elif source == Sources.risuai:
            result = RisuaiRandomOrLatestResponseItem(**card_data)
        elif source == Sources.webring:
            result = WebringRandomOrLatestResponseItem(data_hash=card_data['card_data_hash'], name=card_data['name'], id=card_data['card_data_hash'], added=card_data['added'], author=card_data['author'])
        elif source == Sources.char_tavern:
            with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(f'SELECT * FROM char_tavern_character WHERE path = %s', (card_data['path'],))
                node_result = cursor.fetchone()
                if node_result is None:
                    continue
            result = CharTavernRandomOrLatestResponseItem(**card_data, id=card_data['path'], tagline=node_result['data']['tagline'])
        else:
            result = GenericRandomOrLatestResponseItem(data_hash=card_data['card_data_hash'], sourceSpecific=card_data['source'], name=card_data['name'], added=card_data['added'], id=card_data['card_data_hash'])
        output.append(result)
    return output


def _select_sql(table_name: str):
    return f"SELECT * FROM {table_name} WHERE (metadata->'safety'->'categories'->>'sexual_minors')::boolean = false OR (metadata->'safety'->'bad_shit'->>'loli')::boolean = false ORDER BY added DESC LIMIT %s"


@bp1.route('/v1/latest-character')
@cache.cached(timeout=GLOBAL_CACHE_SECONDS, query_string=True)
@limiter.limit('1 per second', key_func=lambda: get_remote_address_proxied('GET_LATEST'))
def latest():
    latest_count, err = parse_int_arg(request.args.get('count', 10), 'count')
    if err:
        return jsonify(ErrorResponse(message=err, code=400).model_dump()), 400
    if latest_count > 10:
        return jsonify(ErrorResponse(message='count cannot be greater than 10', code=400).model_dump()), 400
    if latest_count < 1:
        return jsonify(ErrorResponse(message='count cannot be less than 1', code=400).model_dump()), 400

    output = []
    try:
        with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(_select_sql('chub_character_def'), (latest_count,))
            output.extend(_parse_query(cursor.fetchall(), Sources.chub))
            cursor.execute(_select_sql('generic_character_def'), (latest_count,))
            output.extend(_parse_query(cursor.fetchall(), Sources.generic))
            cursor.execute(_select_sql('booru_character_def'), (latest_count,))
            output.extend(_parse_query(cursor.fetchall(), Sources.booru))
            cursor.execute(_select_sql('nyaime_character_def'), (latest_count,))
            output.extend(_parse_query(cursor.fetchall(), Sources.nyaime))
            cursor.execute(_select_sql('risuai_character_def'), (latest_count,))
            output.extend(_parse_query(cursor.fetchall(), Sources.risuai))
            cursor.execute(_select_sql('webring_character_def'), (latest_count,))
            output.extend(_parse_query(cursor.fetchall(), Sources.webring))
            cursor.execute(_select_sql('char_tavern_character_def'), (latest_count,))
            output.extend(_parse_query(cursor.fetchall(), Sources.char_tavern))
    except:
        _logger.error(traceback.format_exc())
        raise
    return jsonify(list(reversed(sorted([x.model_dump() for x in output], key=lambda d: parse(d['added']))))[:latest_count])

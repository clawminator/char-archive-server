import logging

from flask import jsonify
from redis import Redis

from . import bp1
from ...config import GLOBAL_CACHE_SECONDS
from ...database.connection import CursorFromConnectionFromPool
from ...flask import limiter, cache, get_remote_address_proxied

_logger = logging.getLogger('SERVER').getChild('INFO')

_r = Redis(host='localhost', port=6379, db=3)


@bp1.route('/v1/info')
@cache.cached(timeout=GLOBAL_CACHE_SECONDS * 2, query_string=True)
@limiter.limit('1 per second', key_func=lambda: get_remote_address_proxied('GET_INFO'))
def info():
    result = {}
    with CursorFromConnectionFromPool() as cursor:
        cursor.execute('SELECT COUNT(*) FROM chub_character')
        result.setdefault('chub', {})['characters'] = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM chub_user')
        result.setdefault('chub', {})['users'] = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM chub_lorebook')
        result.setdefault('chub', {})['lorebooks'] = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM generic_character_def')
        result.setdefault('generic', {})['characters'] = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM booru_character_def')
        result.setdefault('booru', {})['characters'] = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM nyaime_character_def')
        result.setdefault('nyaime', {})['characters'] = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM risuai_character_def')
        result.setdefault('risuai', {})['characters'] = cursor.fetchone()[0]

    # As of Oct 23, 2024.
    result['plap_costs'] = {
        'calculated': 0.0,
        'drago_adj': 1.35,
        'base_adj': 1.5
    }

    # Dynamic costs are disabled since there is only 1 proxy online now
    # and I'm not going to keep adding new model costs.
    # How far we've fallen...
    # plap_costs_data = _r.get('plap_costs')
    # if plap_costs_data:
    #     grand_total, _ = pickle.loads(plap_costs_data)
    #     result['plap_costs']['calculated'] = grand_total
    result['plap_costs']['calculated'] = 9406976.55

    return jsonify(result)

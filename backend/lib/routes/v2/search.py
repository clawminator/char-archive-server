import json
import logging
import traceback

from flask import jsonify, Response

from lib.flask import limiter, get_remote_address_proxied, cache
from lib.meilisearch.client import MeilisearchClient
from lib.routes.v1.response_types.error import ErrorResponse
from lib.routes.v2 import bp2

_MAX_SEARCH_RESULTS = 20

_logger = logging.getLogger('SERVER').getChild('SEARCH V2')


@bp2.route('/v2/search/query')
# This route is not cached because there is not a simple way to prevent caching errors. The edge/CDN will handle caching.
# @cache.cached(timeout=GLOBAL_CACHE_SECONDS, query_string=True)
@limiter.limit('1 per second', key_func=lambda: get_remote_address_proxied('DO_SEARCH'))
def search_v2():
    return jsonify(ErrorResponse(message='v2 search endpoint has been depreciated', code=404).model_dump()), 404


@bp2.route('/v2/search/tags')
@cache.cached(timeout=86400, query_string=True)
@limiter.limit('1 per second', key_func=lambda: get_remote_address_proxied('GET_SEARCH_TAGS'))
def search_tags():
    try:
        result = sorted([(x[0].strip(), x[1]) for x in MeilisearchClient.aggs('tags') if x[0]])
        response = Response(json.dumps(result, separators=(',', ':')), mimetype='application/json')
        return response
    except:
        _logger.error(f'Meilisearch error: {traceback.format_exc()}')
        return ErrorResponse(message='search backend broken', code=500), 500

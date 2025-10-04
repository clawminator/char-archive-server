import logging

from flask import jsonify

from lib.flask import cache, limiter, get_remote_address_proxied
from lib.routes.v1 import bp1
from lib.routes.v1.response_types.error import ErrorResponse
from lib.search.keywords import search_keywords

_logger = logging.getLogger('SERVER').getChild('SEARCH V1')


@bp1.route('/v1/search/query')
# This route is not cached because there is not a simple way to prevent caching errors. The edge/CDN will handle caching.
# @cache.cached(timeout=GLOBAL_CACHE_SECONDS, query_string=True)
@limiter.limit('1 per second', key_func=lambda: get_remote_address_proxied('DO_SEARCH'))
def search_v1():
    return jsonify(ErrorResponse(message='v1 search endpoint has been depreciated', code=404).model_dump()), 404


@bp1.route('/v1/search/tags')
@cache.cached(timeout=86400, query_string=True)
@limiter.limit('1 per second', key_func=lambda: get_remote_address_proxied('GET_SEARCH_TAGS'))
def search_tags():
    return jsonify(ErrorResponse(message='v1 tags endpoint has been depreciated', code=404).model_dump()), 404


@bp1.route('/v1/search/keys')
@cache.cached(timeout=604800, query_string=True)
def search_keys():
    return jsonify(search_keywords())

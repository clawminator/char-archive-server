import json
import logging
import traceback

from flask import jsonify, request, Response

from lib.flask import limiter, get_remote_address_proxied, cache
from lib.meilisearch.client import MeilisearchClient
from lib.routes.v1.response_types.error import ErrorResponse
from lib.routes.v3 import bp3
from lib.routes.v3.searches.meilisearch import meilisearch_search_v3
from lib.routes.v3.searches.natural import meilisearch_natural_v3
from lib.routes.v3.searches.parse_search import parse_query_backend
from lib.routes.v3.searches.shared_v3 import shared_v3_search_logic
from lib.sources import Sources

_MAX_SEARCH_RESULTS = 20

_logger = logging.getLogger('SERVER').getChild('SEARCH V3')


@bp3.route('/v3/search/query')
# This route is not cached because there is not a simple way to prevent caching errors. The edge/CDN will handle caching.
@limiter.limit('1 per second', key_func=lambda: get_remote_address_proxied('DO_SEARCH'))
def search_v3():
    stuff = shared_v3_search_logic()

    if len(stuff) == 2:
        return stuff[0], stuff[1]
    page_arg, page_size_arg, sort_by_arg, sort_direction_arg, exclude_forks, comparisons, query_arg = stuff

    search_method: str
    if request.args.get('natural', 'false').lower() == 'true':
        result, total_pages = meilisearch_natural_v3(query_arg, page_arg, page_size_arg, sort_by_arg, sort_direction_arg, exclude_forks)
        search_method = 'natural'
        parsed_query_str = None
    else:
        try:
            parsed_query_str = parse_query_backend(query_arg)
        except:
            _logger.error(f'Search query parsing failed: "{query_arg}"\n{traceback.format_exc()}')
            return jsonify(ErrorResponse(message='failed to decode search query arg', code=400).model_dump()), 400
        result, total_pages = meilisearch_search_v3(parsed_query_str, page_arg, page_size_arg, sort_by_arg, sort_direction_arg, exclude_forks, comparisons)
        search_method = 'meilisearch'

    if isinstance(result, ErrorResponse):
        # For debug
        # x = result.model_dump()
        # x['parsed'] = parsed_query_str
        # x['query'] = query_arg
        # return jsonify(x), 400
        return jsonify(result.model_dump()), 400

    for item in result:
        if item.source != Sources.chub.value:
            del item.chub

    loli_count = 0
    for item in result:
        if item.safety.bad_shit.loli:
            loli_count += 1
        del item.safety
    loli_percent = loli_count / len(result) if loli_count > 0 else 0

    search_results = [json.loads(x.model_dump_json()) for x in result]

    # Rename chub fields to match what the node route returns.
    for i in range(len(search_results)):
        result = search_results[i]
        if result.get('chub'):
            search_results[i]['chub'] = {
                'fullPath': result['chub']['chub_fullPath'],
                'fork': result['chub']['chub_fork'],
                'anonymousAuthor': result['chub']['chub_anonymousAuthor']  # TODO: remove .get() and just use normal
            }

    # if total_pages > 100:
    #     total_pages = 100

    return jsonify({
        'result': search_results,
        'totalPages': total_pages,
        'safety': {
            'loli': round(loli_percent, 2)
        },
        'searchMethod': search_method,
        'parsedQuery': parsed_query_str
    })


@bp3.route('/v2/search/tags')
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

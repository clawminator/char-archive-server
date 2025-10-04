import logging

from flask import jsonify

from lib.config import GLOBAL_CACHE_SECONDS
from lib.flask import cache, limiter, get_remote_address_proxied
from lib.routes.v1 import bp1
from lib.routes.v1.handlers.match import match_handler
from lib.routes.v1.response_types.error import ErrorResponse

_logger = logging.getLogger('SERVER').getChild('RATINGS')


@bp1.route('/v1/<string:site>/ratings')
@bp1.route('/v1/<string:site>/ratings/<string:node_type>/<path:p>')
@cache.cached(timeout=GLOBAL_CACHE_SECONDS, query_string=True)
@limiter.limit('1 per second', key_func=lambda: get_remote_address_proxied('GET_RATINGS'))
def ratings(site=None, node_type=None, p=None):
    if not site or not node_type or not p:
        return jsonify(ErrorResponse(message='must specify the path', code=400).model_dump()), 400
    if node_type not in ['character', 'lorebook']:
        return jsonify(ErrorResponse(message='invalid node type', code=400).model_dump()), 400
    parts = p.split('/')

    handler_class = match_handler(site)
    if not handler_class:
        return jsonify(ErrorResponse(message='invalid site identifier', code=400).model_dump()), 400
    handler = handler_class(parts, node_type, 0)
    check_code, check_error = handler.check_parts()
    if check_error or check_code != 200:
        return jsonify(ErrorResponse(message=check_error, code=check_code).model_dump()), 400

    try:
        ratings_result, status_code, ratings_err = handler.handle_ratings()
        if ratings_err:
            return jsonify(ErrorResponse(message=ratings_err, code=status_code).model_dump()), 400

        # The response is not typed so that the handlers can return whatever format the site stores their ratings/comments in.
        return jsonify(ratings_result)
    except NotImplementedError:
        return jsonify(ErrorResponse(message='ratings are not available for this site', code=400).model_dump()), 400

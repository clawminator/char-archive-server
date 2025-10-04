import logging

from flask import jsonify, request

from . import bp1
from .handlers.match import match_handler
from .response_types.error import ErrorResponse
from ...config import GLOBAL_CACHE_SECONDS
from ...flask import cache, limiter
from ...helpers.args import parse_int_arg

_logger = logging.getLogger('SERVER').getChild('DEFINITION')


@bp1.route('/v1/<string:site>/def/<path:path>')
@bp1.route('/v1/<string:site>/def')
@cache.cached(timeout=GLOBAL_CACHE_SECONDS, query_string=True)
@limiter.limit('1 per second', key_func=lambda: 'GET_DEFINITION')
def definition(site=None, path=None):
    if not path or not site:
        return jsonify(ErrorResponse(message='must specify the path', code=400).model_dump()), 400
    parts = path.split('/')

    version, version_err = parse_int_arg(request.args.get('version', 0), 'version')
    if version_err:
        return jsonify(ErrorResponse(message=version_err, code=400).model_dump()), 400

    original_unmodified_arg = request.args.get('unmodified') == 'true'
    node_type = parts.pop(0)

    handler_class = match_handler(site)
    if not handler_class:
        return jsonify(ErrorResponse(message='invalid site identifier', code=400).model_dump()), 400
    handler = handler_class(parts, node_type, version)
    check_code, check_error = handler.check_parts()
    if check_error or check_code != 200:
        return jsonify(ErrorResponse(message=check_error, code=check_code).model_dump()), 400

    card_def, response_code, def_err = handler.handle_def(original_unmodified_arg)
    if def_err:
        return jsonify(ErrorResponse(message=def_err, code=check_code).model_dump()), 400
    return jsonify(card_def), response_code

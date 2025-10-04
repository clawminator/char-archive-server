import io
import logging
import traceback
from datetime import datetime, timezone

from PIL import Image
from flask import jsonify, request

from lib.config import GLOBAL_CACHE_SECONDS
from lib.flask import cache, limiter, get_remote_address_proxied
from lib.routes.v1 import bp1
from lib.routes.v1.handlers.match import match_handler
from lib.routes.v1.response_types.error import ErrorResponse
from lib.routes.v1.response_types.node import NodeResponse
from lib.sources import Sources

_logger = logging.getLogger('SERVER').getChild('NODE')


@bp1.route('/v1/<string:site>/node')
@bp1.route('/v1/<string:site>/node/<string:node_type>/<path:p>')
@cache.cached(timeout=GLOBAL_CACHE_SECONDS, query_string=True)
@limiter.limit('5 per second', key_func=lambda: get_remote_address_proxied('GET_NODE'))
def node(site=None, node_type=None, p=None):
    if not site or not node_type or not p:
        return jsonify(ErrorResponse(message='must specify the path', code=400).model_dump()), 400
    if node_type not in ['character', 'lorebook']:
        return jsonify(ErrorResponse(message='invalid node type', code=400).model_dump()), 400
    parts = p.split('/')

    include_node_arg = request.args.get('node', False)

    handler_class = match_handler(site)
    if not handler_class:
        return jsonify(ErrorResponse(message='invalid site identifier', code=400).model_dump()), 400
    handler = handler_class(parts, node_type, version=0)
    check_code, check_error = handler.check_parts()
    if check_error or check_code != 200:
        return jsonify(ErrorResponse(message=check_error, code=check_code).model_dump()), 400

    result, status_code, node_err = handler.handle_node()
    if node_err:
        return jsonify(ErrorResponse(message=node_err, code=status_code).model_dump()), 400
    image_bytes, _, img_err = handler.handle_image()

    result['image'] = {
        'width': None,
        'height': None,
    }
    if img_err:
        result['image']['error'] = img_err
    else:
        try:
            img = Image.open(io.BytesIO(image_bytes))
            result['image']['width'] = img.width
            result['image']['height'] = img.height
        except:
            result['image']['error'] = 'unknown error reading image bytes to determine dimensions'
            _logger.warning(traceback.format_exc())

    if isinstance(result.get('added'), datetime):
        result['added'] = result['added'].astimezone(timezone.utc).isoformat()
    if isinstance(result.get('updated'), datetime):
        result['updated'] = result['updated'].astimezone(timezone.utc).isoformat()

    node_response = NodeResponse(**result).model_dump()

    if not request.args.get('chats'):
        del node_response['chats']
    if not request.args.get('ratings'):
        del node_response['ratings']
    if site != Sources.chub.value:
        del node_response['chub']
    if not include_node_arg:
        del node_response['node']

    return jsonify(node_response)

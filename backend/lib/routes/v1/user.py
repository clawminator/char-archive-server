from urllib.parse import unquote

from flask import jsonify

from . import bp1
from .handlers.match import match_handler
from .response_types.error import ErrorResponse
from .response_types.user import UserResponse
from ...config import GLOBAL_CACHE_SECONDS
from ...flask import cache, limiter, get_remote_address_proxied


@bp1.route('/v1/<string:site>/user')
@bp1.route('/v1/<string:site>/user/<string:username>')
@cache.cached(timeout=GLOBAL_CACHE_SECONDS, query_string=True)
@limiter.limit('1 per second', key_func=lambda: get_remote_address_proxied('GET_USER'))
def user(site=None, username=None):
    if not site or not username:
        return jsonify(ErrorResponse(message='must specify the path', code=400).model_dump()), 400
    username = unquote(unquote(unquote(username)))

    handler_class = match_handler(site)
    if not handler_class:
        return jsonify(ErrorResponse(message='invalid site identifier', code=404).model_dump()), 400
    handler = handler_class([], 'character', 0)
    user_data = handler.handle_user(username)

    if user_data is None or (not len(user_data['characters']) and not len(user_data['lorebooks'])):
        return jsonify(ErrorResponse(message='user not found', code=404).model_dump()), 400
    return jsonify(UserResponse(**user_data).model_dump())

import json
import sys

from flask import Response

from lib.flask import get_remote_address_proxied, limiter
from lib.routes.v1 import bp1


@bp1.route('/v1/health')
@limiter.limit('999 per second', key_func=lambda: get_remote_address_proxied('GET_HEALTH'))
def health():
    resp = Response(json.dumps({'health': 'ok'}))
    resp.headers['Content-Type'] = 'application/json'
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

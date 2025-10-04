import logging

from flask import Flask, request
from flask_caching import Cache
from flask_limiter import Limiter

_logger = logging.getLogger('SERVER').getChild('FLASK')


def get_remote_address_proxied(key: str = '') -> str:
    if 'CF-Connecting-IP' in request.headers:
        ip = request.headers['CF-Connecting-IP']
    elif 'X-Forwarded-For' in request.headers:
        # X-Forwarded-For might contain multiple IP addresses, return the first one.
        ip = request.headers['X-Forwarded-For'].split(',')[0]
    else:
        ip = request.remote_addr or "127.0.0.1"
    return ip + key


app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': 'redis://localhost:6379/0', 'CACHE_KEY_PREFIX': 'api_server__'})

# NOTE: rate limiting doesn't work for all requests because there is application and CDN caching.
limiter = Limiter(
    get_remote_address_proxied,
    app=app,
    default_limits=['1 per second'],
    storage_uri="redis://localhost:6379",
    storage_options={"socket_connect_timeout": 30},
    strategy="fixed-window",
)

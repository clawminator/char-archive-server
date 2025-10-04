#!/usr/bin/env python3
import logging
import os
import sys
import traceback

from flask import jsonify, request

from lib.config import GLOBAL_SEARCH_INDEX, ALLOWED_EXTERNAL_CORS_ORIGINS
from lib.database.connection import Database
from lib.flask import app, limiter
from lib.flask import cache
from lib.meilisearch.client import MeilisearchClient
from lib.meilisearch.consts import MEILISEARCH_HOST, MEILISEARCH_MASTER_KEY
from lib.routes.v1 import bp1
from lib.routes.v1.response_types.error import ErrorResponse
from lib.routes.v2 import bp2
from lib.routes.v3 import bp3

cache.clear()
limiter.reset()
app.register_blueprint(bp1, url_prefix='/api/archive/')
app.register_blueprint(bp2, url_prefix='/api/archive/')
app.register_blueprint(bp3, url_prefix='/api/archive/')

logging.basicConfig()
logger = logging.getLogger('SERVER')
logger.setLevel(logging.INFO)

with app.app_context():
    logger.info('Starting Meilisearch connection')
    try:
        MeilisearchClient.connect(MEILISEARCH_HOST)
        MeilisearchClient.initialise(MEILISEARCH_HOST, GLOBAL_SEARCH_INDEX, MEILISEARCH_MASTER_KEY)
    except:
        logger.error(f'Failed to start Meilisearch connection: {traceback.format_exc()}')
        sys.exit(1)

    logger.info('Starting database connection')
    try:
        Database.initialise(minconn=1, maxconn=100, host=os.environ.get('DATABASE_IP', '127.0.0.1'), database='char_archive', user='char_archive', password='hei3ucheet5oochohjongeisahV3mei0')
    except:
        logger.error(f'Failed to start database connection: {traceback.format_exc()}')
        sys.exit(1)


@app.route('/')
@app.route('/<first>')
@app.route('/<first>/<path:rest>')
def fallback(first=None, rest=None):
    return jsonify(ErrorResponse(message='not an endpoint', code=404).model_dump()), 404


@app.errorhandler(500)
def server_error(e):
    app.logger.error(e)
    return jsonify(ErrorResponse(message='Internal Server Error :(', code=500).model_dump()), 500


@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify(ErrorResponse(message='too many requests', code=429).model_dump()), 429


@app.after_request
def apply_cors(response):
    # Defaults
    if request.headers.get('Host') in ['127.0.0.1:5500', 'localhost:5500', '172.0.3.101:5500', 'localhost:5173']:
        response.headers['Access-Control-Allow-Origin'] = '*'
    else:
        response.headers['Access-Control-Allow-Origin'] = 'https://char-archive.example.com'

    # Check if the origin is in the allowed list
    origin = request.headers.get('Origin')
    if origin in ALLOWED_EXTERNAL_CORS_ORIGINS:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'

    return response


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5500)

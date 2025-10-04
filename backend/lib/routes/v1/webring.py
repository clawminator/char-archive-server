import mimetypes
import os

import requests
from bs4 import BeautifulSoup
from flask import jsonify, Response
from psycopg2.extras import RealDictCursor

from . import bp1
from ...config import CARD_IMAGE_ROOT_DIR, GLOBAL_CACHE_SECONDS
from ...database.connection import CursorFromConnectionFromPool
from ...flask import limiter, get_remote_address_proxied, cache

_WEBRING_ICONS_PATH = CARD_IMAGE_ROOT_DIR.parent / 'webring/icons'


@bp1.route('/v1/webring/icon/<domain>')
@cache.cached(timeout=GLOBAL_CACHE_SECONDS * 2, query_string=True)
@limiter.limit('1 per second', key_func=lambda: get_remote_address_proxied('GET_WEBRING_ICON'))
def webring_favicon(domain):
    with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
        cursor.execute('SELECT * FROM webring_character_def where author = %s LIMIT 1', (domain,))
        data = cursor.fetchone()
    if not data:
        return jsonify({'error': 'website not valid'}), 400

    # Check if the icon already exists
    icon_path = os.path.join(_WEBRING_ICONS_PATH, f'{domain}.ico')
    if os.path.exists(icon_path):
        with open(icon_path, 'rb') as file:
            icon_data = file.read()
        mime_type, _ = mimetypes.guess_type(icon_path)
        return Response(icon_data, mimetype=mime_type)

    print('fetching for', domain)

    url = f'https://{domain}'
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        icon_link = soup.find('link', rel='icon')

        if icon_link:
            icon_url = icon_link['href']
            if not icon_url.startswith('http'):
                icon_url = url + '/' + icon_url.lstrip('/')

            icon_response = requests.get(icon_url)
            if icon_response.status_code == 200:
                # Save the icon to the specified path
                with open(icon_path, 'wb') as file:
                    file.write(icon_response.content)

                with open(icon_path, 'rb') as file:
                    icon_data = file.read()
                mime_type, _ = mimetypes.guess_type(icon_path)
                return Response(icon_data, mimetype=mime_type)

    # Return 200 because that will make CF cache it and also it's not an error since the frontend
    # will display the webring logo.
    return jsonify({'error': 'icon or website not found'}), 200

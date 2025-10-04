from time import mktime
from wsgiref.handlers import format_date_time

import markdown
from flask import jsonify, request, Response

from . import bp1
from ...database.connection import CursorFromConnectionFromPool
from ...flask import cache, limiter, get_remote_address_proxied


@bp1.route('/v1/aicg-chronicles')
@cache.cached(timeout=120, query_string=True)
@limiter.limit('1 per second', key_func=lambda: get_remote_address_proxied('GET_AICG_CHRONICLES'))
def aicg_chronicles():
    url = request.args.get('url')
    if not url:
        return jsonify({'message': 'url is required'}), 400

    with CursorFromConnectionFromPool() as cursor:
        cursor.execute(f"SELECT text, timestamp FROM aicg_chronicles WHERE url = %s ORDER BY timestamp DESC LIMIT 1", (url,))
        row = cursor.fetchone()
    if not row:
        return jsonify({'message': 'url not matched'}), 400
    text, timestamp = row

    if request.args.get('render') == 'true':
        md = markdown.markdown(text, extensions=['tables'])
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{url}</title>
</head>
<style>
    .container, img {{
        max-width: 100%;
    }}
</style>
<body>
<div class="container">
    {md}
</div>
</body>
</html>"""
        resp = Response(html)
        resp.headers['Content-Type'] = 'text/html'
    else:
        resp = Response(text)
        resp.headers['Content-Type'] = 'text/plain'

    resp.headers['Last-Modified'] = format_date_time(mktime(timestamp.timetuple()))
    return resp

import io
import logging
import traceback
from pathlib import Path

from PIL import Image, ImageFilter
from flask import jsonify, request, Response

from . import bp1
from .handlers.handler import Handler
from .handlers.match import match_handler
from .response_types.error import ErrorResponse
from ...char_card import generate_png_chara
from ...config import CARD_IMAGE_ROOT_DIR
from ...flask import limiter, get_remote_address_proxied, cache
from ...helpers.args import parse_int_arg

_logger = logging.getLogger('SERVER').getChild('IMAGE')


def center_crop(img: Image, landscape_only: bool = False) -> Image:
    """
    Crop a landscape image to square. Ignore portrait.
    """
    width, height = img.size
    if (landscape_only and width > height) or not landscape_only:
        length = min(width, height)
        left = (width - length) / 2
        top = (height - length) / 2
        right = (width + length) / 2
        bottom = (height + length) / 2
        return img.crop((left, top, right, bottom))
    else:
        return img


@limiter.limit('1 per second', key_func=lambda: get_remote_address_proxied('GET_IMAGE_DEF'))
def limit_img_definition():
    """
    Call this function to trigger the rate limiting when a card definition is downloaded.
    """
    return


@bp1.route('/v1/<string:site>/image')
@bp1.route('/v1/<string:site>/image/<string:node_type>/<path:path>')
@bp1.route('/v1/image/<string:image_hash>')
@cache.cached(timeout=604800, query_string=True)  # cache for 7 days
@limiter.limit('1000 per minute', key_func=lambda: get_remote_address_proxied('GET_IMAGE'))
def image(site=None, node_type=None, path=None, image_hash=None):
    if (site is None and (node_type is None or path is None)) and not image_hash:
        return jsonify(ErrorResponse(message='invalid path', code=400).model_dump()), 400
    if not image_hash and node_type not in ['character', 'lorebook']:
        return jsonify(ErrorResponse(message='invalid node type', code=400).model_dump()), 400

    img_format_arg = request.args.get('format', 'PNG').upper()
    if img_format_arg not in ['PNG', 'JPEG']:
        return jsonify(ErrorResponse(message='invalid image format. Allowed: png, jpeg', code=400).model_dump()), 400

    version, version_err = parse_int_arg(request.args.get('version', 0), 'version')
    if version_err:
        return jsonify(ErrorResponse(message=version_err, code=400).model_dump()), 400

    if not path:
        path = ''
    parts = path.split('/')

    handler: Handler = None
    if image_hash:
        img_path = Path(CARD_IMAGE_ROOT_DIR, image_hash[0], image_hash[1], image_hash[2], image_hash[3:])
        if not img_path.is_file():
            return jsonify(ErrorResponse(message='file not found', code=500).model_dump()), 400
        image_bytes = img_path.read_bytes()
    else:
        handler_class = match_handler(site)
        if not handler_class:
            return jsonify(ErrorResponse(message='invalid site identifier', code=400).model_dump()), 400
        handler = handler_class(parts, node_type, version)
        del parts  # don't allow this to be used for anything else
        check_code, check_error = handler.check_parts()
        if check_error or check_code != 200:
            return jsonify(ErrorResponse(message=check_error, code=check_code).model_dump()), 400
        image_bytes, img_status, img_err = handler.handle_image()
        if img_err:
            return jsonify(ErrorResponse(message=img_err, code=img_status).model_dump()), 400

    try:
        img = Image.open(io.BytesIO(image_bytes))
    except:
        _logger.warning(traceback.format_exc())
        return jsonify(ErrorResponse(message='unknown error reading image bytes', code=500).model_dump()), 500

    response_bytes_io = io.BytesIO()

    square_arg = request.args.get('square') == 'true'
    thumbnail_arg = request.args.get('thumbnail') == 'true'
    blur_arg = request.args.get('blur') == 'true'
    optimize_arg = request.args.get('optimize') == 'true'
    def_arg = request.args.get('definition') == 'true'

    if request.args.get('max'):
        max_width, max_width_err = parse_int_arg(request.args.get('max'), 'max')
        if max_width_err:
            return jsonify(ErrorResponse(message=max_width_err, code=400).model_dump()), 400
        if square_arg:
            img = center_crop(img)
        img.thumbnail((max_width, max_width))

    if thumbnail_arg:
        if blur_arg:
            img = img.filter(ImageFilter.GaussianBlur(radius=2))
        if optimize_arg:
            img = img.quantize(colors=64).convert('RGB')
        img.save(response_bytes_io, format=img_format_arg, optimize=optimize_arg)
    elif handler and def_arg:
        limit_img_definition()
        card_def, response_code, def_err = handler.handle_def(original_unmodified=False)
        if def_err:
            return jsonify(ErrorResponse(message=def_err, code=response_code).model_dump()), 400
        metadata = generate_png_chara(card_def)
        img.save(response_bytes_io, format=img_format_arg, pnginfo=metadata)
    else:
        img.save(response_bytes_io, format=img_format_arg)

    response_bytes_io.seek(0)
    resp = Response(response_bytes_io)
    resp.headers['Content-Type'] = f'image/{img_format_arg.lower()}'
    return resp

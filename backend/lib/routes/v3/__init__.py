import logging

from flask import Blueprint, request
from flask import jsonify

from lib.routes.v1.response_types.error import ErrorResponse

_logger = logging.getLogger('SERVER').getChild('ERROR')
bp3 = Blueprint('v3', __name__)


@bp3.after_request
def apply_content_disposition(response):
    filename_arg = request.args.get('download-filename')
    content_type = response.headers.get('Content-Type')
    if filename_arg and content_type:
        file_type = content_type.split('/')[-1]
        constructed_filename = f'{filename_arg}.{file_type}'
        if filename_arg:
            constructed_filename = filename_arg
        response.headers['Content-Disposition'] = f'attachment; filename="{constructed_filename}"'
    return response


# @bp.before_request
# def ratelimit():
#     print(get_remote_address())


@bp3.errorhandler(500)
def server_error(e):
    _logger.error(f'Internal Error: {e}')
    return jsonify(ErrorResponse(message='Internal Server Error :(', code=500).model_dump()), 500


from . import search

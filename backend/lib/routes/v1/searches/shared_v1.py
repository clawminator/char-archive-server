from flask import jsonify, request

from lib.config import MAX_SEARCH_RESULTS
from lib.helpers.args import parse_int_arg, double_decode_url_param
from lib.routes.v1.response_types.error import ErrorResponse
from lib.routes.v1.searches.chub import parse_chub_item
from lib.search.search_item import all_valid_search_keys


def shared_v1_search_logic():
    page_size_arg, err = parse_int_arg(request.args.get('count', MAX_SEARCH_RESULTS), 'count')
    if err:
        return jsonify(ErrorResponse(message=err, code=400).model_dump()), 400
    if page_size_arg > MAX_SEARCH_RESULTS:
        return jsonify(ErrorResponse(message=f'count cannot be greater than {MAX_SEARCH_RESULTS}', code=400).model_dump()), 400
    page_arg, err = parse_int_arg(request.args.get('page', 1), 'page')
    if err:
        return jsonify(ErrorResponse(message=err, code=400).model_dump()), 400

    sort_by_arg = request.args.get('sort-key')
    sort_direction_arg = request.args.get('sort-dir')
    if sort_direction_arg is not None and sort_direction_arg not in ['asc', 'desc']:
        return jsonify(ErrorResponse(message='invalid sort direction', code=400).model_dump()), 400
    if sort_direction_arg and not sort_by_arg:
        return jsonify(ErrorResponse(message='must supply sort by argument if using sort direction arg', code=400).model_dump()), 400

    forks_arg = request.args.get('forks')
    if forks_arg and forks_arg not in ['true', 'false']:
        return jsonify(ErrorResponse(message='forks argument is either true or false', code=400).model_dump()), 400
    exclude_forks = forks_arg == 'false'

    if sort_by_arg is not None and sort_by_arg.startswith('chub_'):
        sort_by_arg = 'chub.' + sort_by_arg

    search_key_args: dict = dict(request.args)
    search_key_args.pop('query', None)
    search_key_args.pop('count', None)
    search_key_args.pop('page', None)
    search_key_args = {k: double_decode_url_param(v) for k, v in search_key_args.items()}

    chub_key_fields = parse_chub_item(search_key_args)

    all_valid_keys = all_valid_search_keys()
    for k, v in search_key_args.copy().items():
        if k not in all_valid_keys:
            search_key_args.pop(k)

    search_key_args.update(chub_key_fields)

    if search_key_args.get('tags'):
        search_key_args['tags'] = [x.strip(' ') for x in search_key_args['tags'].split(',')]

    query_arg = request.args.get('query')
    if not len(query_arg) and not len(list(search_key_args.keys())):
        return jsonify(ErrorResponse(message='must specify search query', code=400).model_dump()), 400

    query_arg = double_decode_url_param(query_arg)

    return page_arg, page_size_arg, sort_by_arg, sort_direction_arg, exclude_forks, search_key_args, query_arg

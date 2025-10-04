import json

from flask import jsonify, request

from lib.config import MAX_SEARCH_RESULTS
from lib.helpers.args import parse_int_arg, double_decode_url_param
from lib.routes.v1.response_types.error import ErrorResponse


def shared_v3_search_logic():
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

    comparison_input = request.args.get('comparison')
    comparisons = []
    if comparison_input:
        try:
            comparison_data = json.loads(double_decode_url_param(comparison_input))
        except:
            return jsonify(ErrorResponse(message='Comparison must be an object with "k", "v", and "c" fields', code=400).model_dump()), 400

        for comp in comparison_data:
            if not isinstance(comp, dict):
                return jsonify(ErrorResponse(message='Comparison must be an object with "k", "v", and "c" fields', code=400).model_dump()), 400
            comparison = comp.get('c')
            key = comp.get('k')
            value = comp.get('v')
            if not all([comparison, key, value]):
                return jsonify(ErrorResponse(message='Comparison must be an object with "k", "v", and "c" fields', code=400).model_dump()), 400
            if comparison not in ['gt', 'lt', 'ge', 'le', 'eq']:
                return jsonify(ErrorResponse(message=f'comparison "{comparison}" must be `gt`, `lt`, `ge`, `le`, or `eq`', code=400).model_dump()), 400
            comparisons.append({
                'comparison': comparison,
                'key': key,
                'value': value
            })

    query_arg = request.args.get('query')
    if not len(query_arg):
        # Allow empty queries
        query_arg = ''
        # return jsonify(ErrorResponse(message='must specify search query', code=400).model_dump()), 400
    query_arg = double_decode_url_param(query_arg)

    return page_arg, page_size_arg, sort_by_arg, sort_direction_arg, exclude_forks, comparisons, query_arg

import logging
import math
import random
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

from flask import jsonify, request

from lib.meilisearch.client import MeilisearchClient
from . import bp1
from .response_types.error import ErrorResponse
from .response_types.random_latest import ChubRandomOrLatestResponseItem, WebringRandomOrLatestResponseItem, CharTavernRandomOrLatestResponseItem, ChubInfo, GenericRandomOrLatestResponseItem, BooruRandomOrLatestResponseItem, NyaimeRandomOrLatestResponseItem, RisuaiRandomOrLatestResponseItem
from ...flask import limiter, get_remote_address_proxied
from ...helpers.args import parse_int_arg, double_decode_url_param
from ...sources import Sources, SOURCES_VALUES

_LOGGER = logging.getLogger('SERVER').getChild('RANDOM')


def _build_model(row: dict):
    source = row['source']
    if source == Sources.chub.value:
        data = row.copy()
        del data['chub']
        result = ChubRandomOrLatestResponseItem(**data, chub=ChubInfo(fullPath=row['chub']['chub_fullPath']))
    elif source in [Sources.generic.value]:
        result = GenericRandomOrLatestResponseItem(sourceSpecific=row['source'], name=row['name'], id=row['id'], added=row['added'])
    elif source == Sources.booru.value:
        result = BooruRandomOrLatestResponseItem(**row)
    elif source == Sources.nyaime.value:
        result = NyaimeRandomOrLatestResponseItem(**row)
    elif source == Sources.risuai.value:
        result = RisuaiRandomOrLatestResponseItem(**row)
    elif source == Sources.webring.value:
        result = WebringRandomOrLatestResponseItem(**row)
    elif source == Sources.char_tavern.value:
        result = CharTavernRandomOrLatestResponseItem(**row)
    else:
        raise Exception(f'Unknown table name: {source}')
    return result


@bp1.route('/v1/random-character')
@limiter.limit('1 per second', key_func=lambda: get_remote_address_proxied('GET_RANDOM'))
def random_char():
    count_arg, err = parse_int_arg(request.args.get('count', 1), 'count')
    if err:
        return jsonify(ErrorResponse(message=err, code=400).model_dump()), 400
    if count_arg > 10:
        return jsonify(ErrorResponse(message='count cannot be greater than 10', code=400).model_dump()), 400

    with ThreadPoolExecutor() as executor:
        futures = []
        for source in SOURCES_VALUES:
            future = executor.submit(_process_random_source, source, count_arg)
            futures.append(future)

        query_result = []
        for future in as_completed(futures):
            query_result.extend(future.result())

    # Since chub.ai constitutes the majority of the archive, these cards will make up
    # a dynamic majority of the results.
    chub_ratio = 1 / 2
    chub_card_count = math.ceil(chub_ratio * count_arg)
    try:
        response_result = random.sample([x for x in query_result if isinstance(x, ChubRandomOrLatestResponseItem)], chub_card_count) + random.sample([x for x in query_result if not isinstance(x, ChubRandomOrLatestResponseItem)], count_arg - chub_card_count)
    except ValueError:
        # Can happen when the search index is not fully populated.
        response_result = random.sample(query_result, count_arg)
        _LOGGER.warning(traceback.format_exc())
    random.shuffle(response_result)

    return jsonify([x.model_dump() for x in response_result])


@bp1.route('/v1/random-character-ultra')
@limiter.limit('1/5 seconds', key_func=lambda: get_remote_address_proxied('GET_RANDOM'))
def random_char_extreme():
    """
    Seperate route since we want to control rate limiting.
    """
    tags_arg = request.args.get('tags')
    tags_arg_dict = {}
    if tags_arg:
        tags_arg_dict = {'tags': double_decode_url_param(tags_arg).split(',')}

    response_result = [_build_model(x).model_dump() for x in MeilisearchClient.random_results(25, additional_fields={'type': 'character'} | tags_arg_dict)]
    return jsonify(response_result)


def _process_random_source(source, count_arg):
    return [_build_model(x) for x in MeilisearchClient.random_results(count_arg, additional_fields={'type': 'character', 'source': source})]

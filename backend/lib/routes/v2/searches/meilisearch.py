import logging
import traceback
from typing import List

from meilisearch.errors import MeilisearchApiError
from pydantic import ValidationError

from lib.meilisearch.client import MeilisearchClient
from lib.routes.v1.response_types.error import ErrorResponse
from lib.routes.v1.response_types.search_result import SearchListingsItem

_MAX_SEARCH_RESULTS = 20

_logger = logging.getLogger('SERVER').getChild('SEARCH V2')


def meilisearch_search(query_arg, page_arg, page_size_arg, sort_by_arg, sort_direction_arg, exclude_forks, search_key_args):
    result: List[SearchListingsItem] = []
    try:
        query_result, total_pages = MeilisearchClient.search(
            query_str=query_arg,
            page=page_arg,
            page_size=page_size_arg,
            exclude_fields=[('chub.chub_fork', True)] if exclude_forks else None,
            sort_field=sort_by_arg,
            sort_direction=sort_direction_arg,
            additional_fields=search_key_args
        )
    except MeilisearchApiError:
        _logger.error(f'Search error: {traceback.format_exc()}')
        return ErrorResponse(message='invalid search parameters', code=400), 400
    except:
        _logger.error(f'Search error: {traceback.format_exc()}')
        return ErrorResponse(message='search backend broken', code=500), 500

    for item in query_result:
        try:
            result.append(SearchListingsItem(**item))
        except ValidationError:
            _logger.error(f'Search failed: {traceback.format_exc()}. {item}')
            MeilisearchClient.client().delete_key(item['id'])

    return result, total_pages

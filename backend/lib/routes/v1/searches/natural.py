import logging
import traceback
from typing import List

import elastic_transport
import elasticsearch
from pydantic import ValidationError

from lib.elastic_client import ElasticClient
from lib.routes.v1 import ErrorResponse
from lib.routes.v1.response_types.search_result import SearchListingsItem


_logger = logging.getLogger('SERVER').getChild('SEARCH NATRUAL')


def natural_search(query_arg, page_arg, page_size_arg, exclude_forks=False):
    result: List[SearchListingsItem] = []
    try:
        query_result, total_pages = ElasticClient.natural_query(
            query_str=query_arg,
            page=page_arg,
            page_size=page_size_arg,
            exclude_fields=[('chub.chub_fork', True)] if exclude_forks else None
        )
    except elastic_transport.ConnectionTimeout:
        return ErrorResponse(message='connection timeout', code=500), 500
    except elasticsearch.BadRequestError as e:
        print(e)
        return ErrorResponse(message='bad search', code=400), 400
    except elasticsearch.ApiError:
        _logger.error(f'Elasticsearch error: {traceback.format_exc()}')
        return ErrorResponse(message='search backend broken', code=500), 500

    for item in query_result:
        try:
            result.append(SearchListingsItem(**item['_source']))
        except ValidationError:
            _logger.error(f'Search failed: {traceback.format_exc()}. {item}')
            ElasticClient.delete_by_id(item['_id'])

    return result, total_pages

import logging
import re
import traceback
from typing import List

import elastic_transport
import elasticsearch
from pydantic import ValidationError

from lib.elastic_client import ElasticClient, CustomElasticException
from lib.routes.v1 import ErrorResponse
from lib.routes.v1.response_types.search_result import SearchListingsItem

_logger = logging.getLogger('SERVER').getChild('SEARCH KEYWORD')


def keyword_search(query_arg, page_arg, page_size_arg, sort_by_arg, sort_direction_arg, exclude_forks, search_key_args):
    result: List[SearchListingsItem] = []
    try:
        query_result, total_pages = ElasticClient.multi_match_search(
            query_arg,
            query_fields=['*'],
            query_fields_exclude=['safety', 'embedding', 'added', 'created', 'updated'],
            exclude_fields=[('chub.chub_fork', True)] if exclude_forks is True else None,
            page=page_arg,
            page_size=page_size_arg,
            additional_fields=search_key_args,
            sort_field=sort_by_arg,
            sort_order=sort_direction_arg
        )
    except elastic_transport.ConnectionTimeout:
        return ErrorResponse(message='connection timeout', code=500), 500
    except elasticsearch.BadRequestError as e:
        print(e)
        msg = e.info['error']['root_cause'][0]['reason']
        if msg.startswith('No mapping found for') and msg.endswith('in order to sort on'):
            key = re.match(r'No mapping found for \[(.*?)\.keyword] in order to sort on', msg)
            return ErrorResponse(message=f'no mapping found for key [{key.group(1)}]', code=400), 400
        print(e)
        return ErrorResponse(message='bad search', code=400), 400
    except elasticsearch.ApiError:
        _logger.error(f'Elasticsearch error: {traceback.format_exc()}')
        return ErrorResponse(message='search backend broken', code=500), 500
    except CustomElasticException as e:
        # Our own exception.
        _logger.error(f'Elasticsearch error: {traceback.format_exc()}')
        return ErrorResponse(message=e.message, code=500), 500

    for item in query_result:
        try:
            result.append(SearchListingsItem(**item['_source']))
        except ValidationError:
            _logger.error(f'Search failed: {traceback.format_exc()}. {item}')
            ElasticClient.delete_by_id(item['_id'])

    return result, total_pages

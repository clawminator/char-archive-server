import json
import logging
import traceback
from typing import List

from meilisearch.errors import MeilisearchApiError
from pydantic import ValidationError

from lib.meilisearch.client import MeilisearchClient
from lib.routes.v1 import ErrorResponse
from lib.routes.v1.response_types.search_result import SearchListingsItem
from lib.search.empty_embedding import EMPTY_EMBEDDING_VECTOR

_logger = logging.getLogger('SERVER').getChild('SEARCH NATRUAL')


def meilisearch_natural_v3(query: str, page_arg: int, page_size_arg: int, sort_by_arg: str, sort_direction_arg: str, exclude_forks: bool):
    result: List[SearchListingsItem] = []
    try:
        query_result, total_pages = MeilisearchClient.search_semantic(
            query=query,
            page=page_arg,
            page_size=page_size_arg,
            exclude_fields=[('chub.chub_fork', True)] if exclude_forks else None,
            sort_field=sort_by_arg,
            sort_direction=sort_direction_arg,
        )
    except MeilisearchApiError:
        _logger.error(f'Search error: {traceback.format_exc()}')
        return ErrorResponse(message='invalid search parameters', code=400), 400
    except:
        _logger.error(f'Search error: {traceback.format_exc()}')
        return ErrorResponse(message='search backend broken', code=500), 500

    for item in query_result:
        try:
            embeddings = item.get('_vectors', {}).get('default', {}).get('embeddings')
            if len(embeddings) and embeddings[0] != EMPTY_EMBEDDING_VECTOR:
                result.append(SearchListingsItem(**item))
        except ValidationError:
            _logger.error(f'Search failed: {traceback.format_exc()}. {json.dumps(item)}')
            MeilisearchClient.index().delete_document(item['doc_id'])

    return result, total_pages

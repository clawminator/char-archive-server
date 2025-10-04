import json
import logging
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Tuple, List, Dict
from urllib.parse import urlparse

from meilisearch import Client
from meilisearch.errors import MeilisearchApiError
from meilisearch.index import Index
from sentence_transformers import SentenceTransformer

from lib.flask import cache
from lib.helpers.ping import ping

_LOGGER = logging.getLogger('MEILISEARCH')

_MODEL = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')


class MeilisearchClient:
    _ms = None
    _meili_host = ''
    _meili_index = ''
    _api_key = ''
    _index: Index = None

    @classmethod
    def client(cls) -> Client:
        return cls._ms

    @classmethod
    def index(cls) -> Index:
        return cls._index

    @classmethod
    def connect(cls, meili_host: str):
        # Wait for Nebula to establish a connection to the host.
        # Meilisearch timeout is 10 seconds and that applies to the initial connection too.
        meilisearch_hostname = urlparse(meili_host).hostname
        ping_success = ping(meilisearch_hostname)
        while not ping_success:
            _LOGGER.info(f'Establishing connection to {meilisearch_hostname}...')
            ping_success = ping(meilisearch_hostname)
            time.sleep(3)
        _LOGGER.info(f'Established connection to {meilisearch_hostname}')

    @classmethod
    def initialise(cls, meili_host: str, meili_index: str, api_key: str, timeout: int = 10):
        cls._meili_host = meili_host
        cls._meili_index = meili_index
        cls._api_key = api_key

        cls._ms = Client(cls._meili_host, cls._api_key, timeout=timeout)
        try:
            cls._index = cls._ms.get_index(meili_index)
        except MeilisearchApiError:
            pass
        _LOGGER.debug(f'Connected to Meilisearch: {cls._ms.health()}')

    @classmethod
    def search(cls, query_str: str, page: int, page_size: int, exclude_fields: List[Tuple[str, Any]] = None,
               sort_field: str = None, sort_direction: str = None, additional_fields: Dict[str, Any] = None):
        filters = []
        if exclude_fields:
            for field, value in exclude_fields:
                filters.append(f"NOT {field} = {_meili_json_dumps(value)}")

        search_params: dict = {
            'offset': (page - 1) * page_size,
            'limit': page_size,
            'filter': _build_filter_expression(additional_fields)
        }

        if sort_field:
            sort_expression = f"{sort_field}:{'asc' if sort_direction == 'asc' else 'desc'}"
            search_params['sort'] = [sort_expression]

        response = cls._index.search(query_str, search_params)
        total_hits = response['estimatedTotalHits']
        total_pages = (total_hits + page_size - 1) // page_size
        hits = response['hits']
        return hits, total_pages

    @classmethod
    def search_structured(
            cls,
            structured_query: List[List[Dict[str, Dict[str, str]]]],
            page: int,
            page_size: int,
            sort_field: str = None,
            exclude_fields: List[Tuple[str, Any]] = None,
            sort_direction: str = None,
            additional_filter: str = None  # New parameter
    ):
        filter_groups = []
        freetext_terms = []
        freetext_excludes = []

        for group in structured_query:
            group_filters = []
            group_freetext_includes = []
            group_freetext_excludes = []
            for condition in group:
                for field, operation in condition.items():
                    if field == 'freetext':
                        include_term = operation.get('include')
                        exclude_term = operation.get('exclude')
                        if include_term:
                            # Collect freetext include terms
                            group_freetext_includes.append(include_term)
                        if exclude_term:
                            # Collect freetext exclude terms
                            group_freetext_excludes.append(exclude_term)
                    else:
                        include = operation.get('include')
                        exclude = operation.get('exclude')
                        if include is not None:
                            group_filters.append(f"{field} = {_meili_json_dumps(include)}")
                        if exclude is not None:
                            group_filters.append(f"NOT {field} = {_meili_json_dumps(exclude)}")

            # Combine group filters with AND
            if group_filters:
                combined_filters = " AND ".join(group_filters)
                # Enclose in parentheses to maintain precedence
                filter_groups.append(f"({combined_filters})")

            # Collect all freetext includes and excludes
            if group_freetext_includes:
                freetext_terms.extend(group_freetext_includes)
            if group_freetext_excludes:
                freetext_excludes.extend(group_freetext_excludes)

        # Combine all group filters with OR
        final_filter = " OR ".join(filter_groups) if filter_groups else None

        # Combine all freetext includes with OR for the query string
        if freetext_terms:
            final_query = " OR ".join(freetext_terms)
        else:
            final_query = ""

        # Handle freetext excludes by adding negations to the query string
        if freetext_excludes:
            exclude_query_parts = []
            for term in freetext_excludes:
                # Detect if the term is a phrase (contains space)
                if ' ' in term:
                    # Wrap the term in quotes for phrase exclusion
                    escaped_term = _escape_meili_query(term).strip('"')
                    exclude_query_parts.append(f'-"{escaped_term}"')
                else:
                    # Single term exclusion
                    escaped_term = _escape_meili_query(term)
                    exclude_query_parts.append(f'-{escaped_term}')
            exclude_query = " ".join(exclude_query_parts)
            if final_query:
                final_query = f"{final_query} {exclude_query}"
            else:
                final_query = exclude_query

        # Integrate additional_filter if provided
        if additional_filter:
            if final_filter:
                final_filter = f"({final_filter}) AND ({additional_filter})"
            else:
                final_filter = additional_filter

        # Handle additional exclude_fields if provided
        if exclude_fields:
            exclude_filters = [f"NOT {field} = {_meili_json_dumps(value)}" for field, value in exclude_fields]
            exclude_filter_expression = " AND ".join(exclude_filters)
            if final_filter:
                final_filter = f"({final_filter}) AND ({exclude_filter_expression})"
            else:
                final_filter = exclude_filter_expression

        # Build additional filter expression from existing search method
        existing_additional_filter = _build_filter_expression(None)

        if existing_additional_filter:
            if final_filter:
                final_filter = f"({final_filter}) AND ({existing_additional_filter})"
            else:
                final_filter = existing_additional_filter

        # Set up search parameters
        search_params = {
            'offset': (page - 1) * page_size,
            'limit': page_size,
        }

        if final_filter:
            search_params['filter'] = final_filter

        if sort_field:
            sort_expression = f"{sort_field}:{'asc' if sort_direction == 'asc' else 'desc'}"
            search_params['sort'] = [sort_expression]

        response = cls._index.search(final_query, search_params)
        total_hits = response.get('estimatedTotalHits', 0)
        total_pages = (total_hits + page_size - 1) // page_size
        hits = response.get('hits', [])
        return hits, total_pages

    @classmethod
    def random_results(cls, count: int, additional_fields: Dict[str, Any] = None):
        def process_offset(offset: int):
            params = {
                'offset': offset,
                'limit': 1,
                'filter': filter_expression
            }
            r = cls._index.search('*', params)
            if len(r['hits']):
                return r['hits'][0]
            return None

        filter_expression = _build_filter_expression(additional_fields)

        # Determine how many documents are applicable to our search filter
        total_docs = _cached_total_docs_for_filter(filter_expression)
        if total_docs < count:
            count = total_docs

        hits = []
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_offset, offset) for offset in random.sample(range(total_docs), count)]
            for future in as_completed(futures):
                hit = future.result()
                if hit is not None:
                    hits.append(hit)

        return hits

    @classmethod
    def search_semantic(cls, query: str, page: int, page_size: int,
                        embedder_name: str = 'default', exclude_fields: List[Tuple[str, Any]] = None,
                        sort_field: str = None, sort_direction: str = None,
                        additional_fields: Dict[str, Any] = None):
        # Encode the query to get the vector
        query_vector = _MODEL.encode(query).tolist()

        # Build the filter expressions
        filters = []
        if exclude_fields:
            for field, value in exclude_fields:
                filters.append(f"NOT {field} = {_meili_json_dumps(value)}")

        if additional_fields:
            filters_expression = _build_filter_expression(additional_fields)
            if filters:
                filters.append(filters_expression)
            else:
                filters = [filters_expression]

        filter_combined = " AND ".join(filters) if filters else None

        # Construct the search parameters
        search_params: dict = {
            'offset': (page - 1) * page_size,
            'limit': page_size,
            'vector': query_vector,
            'hybrid': {
                'embedder': embedder_name,
                'semanticRatio': 1.0
            },
            'retrieveVectors': True
        }

        if filter_combined:
            search_params['filter'] = filter_combined

        if sort_field:
            sort_expression = f"{sort_field}:{'asc' if sort_direction == 'asc' else 'desc'}"
            search_params['sort'] = [sort_expression]

        # Perform the search with an empty query string or a special keyword if required
        response = cls._index.search('', search_params)

        # Handle the response
        total_hits = response.get('estimatedTotalHits', 0)
        total_pages = (total_hits + page_size - 1) // page_size
        hits = response.get('hits', [])
        return hits, total_pages

    # ===================================================================================================
    # Helper Methods

    @classmethod
    def doc_exists(cls, doc_id: str) -> bool:
        try:
            _ = cls.index().get_document(doc_id)
            return True
        except MeilisearchApiError as e:
            if e.code == 'document_not_found':
                return False
            else:
                raise

    @classmethod
    def aggs(cls, term: str):
        search_params = {
            'facets': [term]
        }
        response = cls._index.search('', search_params)
        facet_distribution = response.get('facetDistribution', {}).get(term, {})
        result = set((key, value) for key, value in facet_distribution.items())
        return result


def _meili_json_dumps(data) -> str:
    return json.dumps(data, ensure_ascii=False)


def _build_filter_expression(additional_fields: Dict[str, Any] | None) -> str:
    filters = []
    if additional_fields:
        for field, value in additional_fields.items():
            if isinstance(value, (list, tuple)):
                for val in value:
                    filters.append(f"{field} = {_meili_json_dumps(val)}")
            else:
                filters.append(f"{field} = {_meili_json_dumps(value)}")

    return " AND ".join(filters)


@cache.memoize(timeout=86400)  # 24 hr
def _cached_total_docs_for_filter(filter_str: str):
    search_params: dict = {
        'filter': filter_str,
        'limit': 0
    }
    response = MeilisearchClient.index().search('*', search_params)
    total_docs = response['estimatedTotalHits']
    return total_docs


def _escape_meili_query(term: str) -> str:
    """
    Escapes special characters in MeiliSearch query except for quotes used for phrases.
    """
    # List of special characters in MeiliSearch that need to be escaped with a backslash
    # Exclude the double quotes since they are handled separately for phrases
    special_chars = r'<>+-=&|!(){}[]^~*?:\/'
    escaped_term = ""
    for char in term:
        if char in special_chars:
            escaped_term += f"\\{char}"
        else:
            escaped_term += char
    return escaped_term

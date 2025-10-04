import json
import logging
import traceback
from datetime import datetime  # Import the class
from typing import List, Any, Dict, Union
from typing import get_origin, get_args

from dateutil import parser as date_parser
from meilisearch.errors import MeilisearchApiError
from pydantic import BaseModel
from pydantic import ValidationError

from lib.meilisearch.client import MeilisearchClient
from lib.routes.v1.response_types.error import ErrorResponse
from lib.routes.v1.response_types.search_result import SearchListingsItem
from lib.search.search_item import SearchChar

_MAX_SEARCH_RESULTS = 20

_logger = logging.getLogger('SERVER').getChild('SEARCH V3')


def meilisearch_search_v3(structured_query: list, page_arg: int, page_size_arg: int, sort_by_arg: str, sort_direction_arg: str, exclude_forks: bool, comparisons: List[Dict[str, Any]]):
    structured_query = _update_chub_keys(structured_query)
    datetime_fields = _get_datetime_fields(SearchChar)

    result: List[SearchListingsItem] = []
    try:
        filter_parts = []
        for comp in comparisons:
            comparison_arg = comp['comparison']
            comparison_key_arg = comp['key']
            comparison_value_arg = comp['value']
            operator_mapping = {
                'gt': '>',
                'ge': '>=',
                'lt': '<',
                'le': '<=',
                'eq': '='
            }
            if comparison_arg not in operator_mapping:
                raise ValueError(f"Invalid comparison operator: {comparison_arg}")
            operator = operator_mapping[comparison_arg]

            # Check if this field is a datetime field
            if comparison_key_arg in datetime_fields:
                if isinstance(comparison_value_arg, str):
                    try:
                        # Parse as datetime
                        parsed_date = date_parser.parse(comparison_value_arg)
                        # Convert to ISO format for Meilisearch
                        processed_value = int(parsed_date.timestamp())
                    except (ValueError, TypeError) as e:
                        raise ValueError(f"Invalid datetime format for field '{comparison_key_arg}': {comparison_value_arg}")
                elif isinstance(comparison_value_arg, datetime):
                    # If it's already a datetime object, convert to ISO format
                    processed_value = int(comparison_value_arg.timestamp())
                else:
                    raise ValueError(f"Field '{comparison_key_arg}' expects a datetime value, got {type(comparison_value_arg).__name__}")
            else:
                # For non-datetime fields
                if isinstance(comparison_value_arg, str) and not comparison_value_arg.isdigit():
                    processed_value = f'"{comparison_value_arg}"'
                else:
                    processed_value = comparison_value_arg

            filter_parts.append(f"{comparison_key_arg} {operator} {processed_value}")

        additional_filter = None
        if filter_parts:
            additional_filter = " AND ".join(filter_parts)

        query_result, total_pages = MeilisearchClient.search_structured(
            structured_query=structured_query,
            page=page_arg,
            page_size=page_size_arg,
            exclude_fields=[('chub.chub_fork', True)] if exclude_forks else None,
            sort_field=sort_by_arg,
            sort_direction=sort_direction_arg,
            additional_filter=additional_filter
        )
    except MeilisearchApiError:
        _logger.error(f'Search error: {traceback.format_exc()}')
        return ErrorResponse(message='invalid search parameters', code=400), 400
    except ValueError as ve:
        _logger.error(f'Invalid comparison parameter: {traceback.format_exc()}')
        return ErrorResponse(message=str(ve), code=400), 400
    except Exception:
        _logger.error(f'Search error: {traceback.format_exc()}')
        return ErrorResponse(message='search backend broken', code=500), 500

    for item in query_result:
        try:
            result.append(SearchListingsItem(**item))
        except ValidationError:
            _logger.error(f'Search failed: {traceback.format_exc()}. {json.dumps(item)}')
            MeilisearchClient.index().delete_document(item['doc_id'])

    return result, total_pages


def _update_chub_keys(obj):
    """
    Chub fields are stored in Meilisearch as `chub.<key name>`.
    Need to append `chub.` to any chub keys in the structured query.
    """
    if isinstance(obj, dict):
        # Create a new dictionary to store the updated key-value pairs
        updated_dict = {}
        for key, value in obj.items():
            if key.startswith('chub_'):
                # Replace 'chub_' with 'chub.chub_' in the key
                new_key = 'chub.' + key
            else:
                new_key = key

            # Recursively process the value
            updated_dict[new_key] = _update_chub_keys(value)
        return updated_dict
    elif isinstance(obj, list):
        # Recursively process each item in the list
        return [_update_chub_keys(item) for item in obj]
    else:
        # Return the value as is for non-dict and non-list objects
        return obj


def _get_datetime_fields(model_class: type[BaseModel]) -> set[str]:
    """Extract all datetime field names from a Pydantic model."""
    datetime_fields = set()

    for field_name, field_info in model_class.model_fields.items():
        field_type = field_info.annotation

        # Handle Optional types (Union[type, None])
        origin = get_origin(field_type)
        if origin is Union:
            args = get_args(field_type)
            # Find the non-None type in the Union
            for arg in args:
                if arg is not type(None):
                    field_type = arg
                    break

        # Check if the field type is datetime
        if field_type is datetime:  # Now this refers to the datetime class
            datetime_fields.add(field_name)

    return datetime_fields

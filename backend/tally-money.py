#!/usr/bin/env python3
import argparse
import csv
import locale
import logging
import pickle
import sys
import traceback
from datetime import datetime
from typing import Union

import elastic_transport
import numpy as np
from elasticsearch.helpers import scan
from elasticsearch_dsl import Search, Q
from pydantic import BaseModel
from redis import Redis
from tqdm import tqdm

from lib.config import ELASTIC_HOST, ELASTIC_API_KEY
from lib.elastic_client import ElasticClient

logging.basicConfig()
logger = logging.getLogger('MAIN')
logger.setLevel(logging.INFO)

_IS_SERVICE = False
_IS_TEST = False
_WRITE_CSVS = False
_USE_REDIS = False

_INDEX_NAME = 'proxy_stats'


class Usage(BaseModel):
    type: str
    cost: Union[float, None] = None
    tokens: int


API_COSTS_PER_1M = {
    # Input, output.
    'turbo': np.mean([1.50, 2.00]),
    'gpt4-turbo': np.mean([10.00, 30.00]),
    'gpt4': np.mean([30.00, 60.00]),
    'gpt4-32k': np.mean([60.00, 120.00]),
    'gpt4o': np.mean([2.5, 10.00]),
    'o1-mini': np.mean([3.00, 12.00]),
    'o1': np.mean([15, 60]),
    'claude': np.mean([8, 24]),
    'claude-sonnet': np.mean([3, 15]),
    'claude-opus': np.mean([15, 75]),
    'gemini': np.mean([0.50, 1.50]),
    'gemini-pro': np.mean([1.25, 5.00]),
    'gemini-flash': np.mean([0.075, 0.30]),
    'mistral-tiny': np.mean([2.5 / 4, 7.5 / 4]),
    'mistral-small': np.mean([2.5 / 3, 7.5 / 3]),
    'mistral-medium': np.mean([2.5 / 2, 7.5 / 2]),
    'mistral-large': np.mean([2.5, 7.5]),
    'aws-claude': np.mean([8, 24]),
    'aws-claude-sonnet': np.mean([3, 15]),
    'aws-claude-opus': np.mean([15, 75]),
    'aws-mistral-small': np.mean([0.001 * 1000, 0.003 * 1000]),
    'aws-mistral-large': np.mean([0.004 * 1000, 0.012 * 1000]),
    'azure-gpt4-32k': np.mean([60.00, 120.00]),
    'azure-gpt4': np.mean([30.00, 60.00]),
    'azure-gpt4-turbo': np.mean([10.00, 30.00]),
    'azure-gpt4o': np.mean([5, 15]),
    'azure-turbo': np.mean([1.5, 2]),
    'gcp-claude': np.mean([np.mean([3, 15]), np.mean([15, 75])]),
    'deepseek': np.mean([0.14, 0.28]),
    'o3-mini': np.mean([1.10, 4.40]),
    'gpt45': np.mean([75.00, 150.00]),

    # These are ignored.
    # Not doing image models because the API returns the tokens, not the number of images generated.
    'dall-e': 0,
    'azure-dall-e': 0,
    'palm-bison': 0,
    'bison': 0,
}


def dynamic_print(msg: str):
    if _IS_SERVICE:
        logger.info(msg)
    else:
        tqdm.write(msg)


def get_unique_urls():
    """
    Retrieves all unique URLs from the specified Elasticsearch index.

    :return: A list of unique URLs
    """
    s = Search(using=ElasticClient().client, index=_INDEX_NAME)
    s.aggs.bucket('unique_urls', 'terms', field='url.keyword', size=10000)
    s = s.extra(size=0)
    response = s.execute()
    unique_urls = [bucket.key for bucket in response.aggregations.unique_urls.buckets if bucket.key != 'proxy.chub-archive.example.com']
    return unique_urls


def process_docs_by_url(batch_size=1000):
    """
    Processes documents for each unique URL in the index, sorted by timestamp.

    :param batch_size: Number of documents to fetch in each batch (default: 1000)
    """
    es_client = ElasticClient().client
    unique_urls = get_unique_urls()
    grand_total = 0
    api_cost_breakdown = {}

    r = None
    if _USE_REDIS:
        r = Redis(host='localhost', port=6379, db=3)

    main_pbar = tqdm(unique_urls, position=0, disable=_IS_SERVICE)

    for url in main_pbar:
        s = Search(using=es_client, index=_INDEX_NAME)
        s = s.query(Q('term', url__keyword=url)).sort({"timestamp": {"order": "asc"}})
        doc_count = s.count()

        if _IS_SERVICE:
            logger.info(f'Processing {doc_count} documents for {url}')

        csv_rows = []
        proxy_api_costs = {}
        total_cost = 0
        previous_doc = None

        docs = scan(es_client, query=s.to_dict(), index=_INDEX_NAME, size=batch_size, preserve_order=True)
        pbar = tqdm(docs, total=doc_count, desc=url, disable=_IS_SERVICE, leave=True, position=1)

        i = 0
        for current_doc in pbar:
            assert current_doc['_source']['url'] == url
            if _IS_TEST and i == 1400:
                previous_doc = None
                break
            i += 1

            current_timestamp = current_doc['_source']['timestamp']
            current_timestamp_d = datetime.fromtimestamp(current_timestamp)

            if previous_doc:
                previous_timestamp = previous_doc['_source']['timestamp']
                previous_timestamp_d = datetime.fromtimestamp(previous_timestamp)
                if current_timestamp_d < previous_timestamp_d:
                    raise Exception(f'ASSERT FAILED: {current_timestamp_d} < {previous_timestamp_d}')
                current_uptime = current_doc['_source']['uptime']
                previous_uptime = previous_doc['_source']['uptime']
                if previous_uptime > current_uptime:
                    # Process and save the previous document's stats (which were before the proxy restarted).
                    new_costs = determine_costs(previous_doc['_source'])
                    added_costs = combine_model_stats({}, new_costs)
                    added_total = calc_total_cost(added_costs)
                    total_cost += added_total
                    api_cost_breakdown = combine_model_stats(api_cost_breakdown, new_costs)
                    timestamp = previous_timestamp_d.strftime('%m-%d-%Y %H:%M')
                    csv_rows.append([new_costs, timestamp, previous_uptime])

            previous_doc = current_doc
            pbar.set_postfix({
                'Timestamp': current_timestamp_d.strftime('%m-%d-%Y %H:%M'),
                'Total Cost': f'{locale.currency(total_cost, grouping=True)}'
            })

        # Process the last document
        if previous_doc:
            new_costs = determine_costs(previous_doc['_source'])
            added_costs = combine_model_stats({}, new_costs)
            added_total = calc_total_cost(added_costs)
            total_cost += added_total
            api_cost_breakdown = combine_model_stats(api_cost_breakdown, new_costs)
            timestamp = datetime.fromtimestamp(previous_doc['_source']['timestamp']).strftime('%m-%d-%Y %H:%M')
            csv_rows.append([new_costs, timestamp, previous_doc['_source']['uptime']])

        grand_total += total_cost
        api_cost_breakdown[url] = proxy_api_costs

        main_pbar.set_postfix({
            'Grand Total': f'{locale.currency(grand_total, grouping=True)}'
        })

        if _WRITE_CSVS and len(csv_rows):
            write_to_csv(csv_rows, filename=f'{url.replace(".", "-")}.csv')
        if _IS_SERVICE:
            logger.info(f'Total cost for {url}: {locale.currency(total_cost, grouping=True)}')

    if _USE_REDIS:
        r.set('plap_costs', pickle.dumps((grand_total, api_cost_breakdown)))
        logger.info('Saved to Redis')

    return grand_total, api_cost_breakdown


def determine_costs(doc):
    costs = {}
    for k, v in doc.items():
        if isinstance(v, dict) and v.get('usage'):
            usage = Usage(type=k, cost=v['usage']['cost'] if v['usage']['cost'] > 0 else None, tokens=v['usage']['tokens'])
            if k not in costs:
                costs[k] = []
            costs[k].append(usage)
    return calculate_costs(costs)


def calculate_costs(data: dict):
    results = {}
    for k, v in data.items():
        if k not in results:
            results[k] = {
                'cost': 0,
                'tokens': 0,
            }
        for x in v:
            if x.cost:
                results[k]['cost'] = results[k]['cost'] + x.cost
            results[k]['tokens'] = results[k]['tokens'] + x.tokens

    for api_type, v in results.items():
        if v['cost'] == 0:
            try:
                v['cost'] = (v['tokens'] / 1_000_000) * API_COSTS_PER_1M[api_type]
            except KeyError as e:
                raise Exception(f'Cost not found for {api_type}: {e}')

    return results


def calc_total_cost(data: dict):
    total = 0
    for k, v in data.items():
        total += v['cost']
    return np.round(total, 2)


def combine_model_stats(dict1: dict, dict2: dict):
    result = {}
    all_models = set(dict1.keys()) | set(dict2.keys())
    for model in all_models:
        result[model] = {
            'cost': (dict1.get(model, {}).get('cost', 0) +
                     dict2.get(model, {}).get('cost', 0)),
            'tokens': (dict1.get(model, {}).get('tokens', 0) +
                       dict2.get(model, {}).get('tokens', 0))
        }
    return result


def write_to_csv(data: list, filename: str):
    all_models = set()
    for row in data:
        all_models.update(row[0].keys())

    header = ['timestamp', 'uptime_seconds'] + [f'{model}_{metric}' for model in sorted(all_models) for metric in ['cost', 'tokens']]

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)

        for row in data:
            model_data = row[0]
            timestamp = row[1]

            if isinstance(timestamp, (int, float)):
                timestamp = datetime.fromtimestamp(timestamp).strftime('%m-%d-%Y %H:%M')

            csv_row = [timestamp]

            # Add uptime (if present, otherwise use 0)
            csv_row.append(row[2] if len(row) > 2 else 0)

            for model in sorted(all_models):
                if model in model_data:
                    csv_row.extend([model_data[model].get('cost', 0), model_data[model].get('tokens', 0)])
                else:
                    csv_row.extend([0, 0])  # Add zeros for missing models

            writer.writerow(csv_row)

    dynamic_print(f"Data has been written to {filename}")


def main(args):
    try:
        ElasticClient.initialise(ELASTIC_HOST, _INDEX_NAME, ELASTIC_API_KEY)
    except elastic_transport.ConnectionError as e:
        logger.critical(f'Failed to connect to Elastic: {e}')
        quit(1)

    locale.setlocale(locale.LC_ALL, '')

    logger.info('Fetching URLs from Elastic...')
    unique_urls = get_unique_urls()
    logger.info(f'Found {len(unique_urls)} unique URLs.')
    grand_total, api_cost_breakdown = process_docs_by_url()
    logger.info(f'Total wasted....... {locale.currency(grand_total, grouping=True)}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--service', action='store_true', help='Run as a service.')
    parser.add_argument('-r', '--redis', action='store_true', help='Store results in Redis.')
    parser.add_argument('-t', '--test', action='store_true')
    parser.add_argument('--write-csv', action='store_true', help='Write the CSVs.')
    args = parser.parse_args()
    _IS_SERVICE = args.service
    _IS_TEST = args.test
    _WRITE_CSVS = args.write_csv
    _USE_REDIS = args.redis
    try:
        main(args)
    except:
        logger.critical(traceback.format_exc())
        sys.exit(1)

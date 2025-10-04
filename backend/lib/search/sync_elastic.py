import concurrent.futures
import logging
import sys
import time
import traceback
from typing import Callable, Any, Tuple, Type

from tqdm import tqdm

from lib.meilisearch.client import MeilisearchClient
from lib.meilisearch.helpers import get_meilisearch_task_with_retries
from lib.search.handlers.base import ElasticHandler

_logger = logging.getLogger('Sync')
_logger.setLevel(logging.INFO)


def _do_print(string: str, is_service: bool):
    if is_service:
        _logger.info(string)
    else:
        tqdm.write(string)


def sync_elastic_source(handler_cls: Type[ElasticHandler], process_row_func: Callable[[ElasticHandler, Any, bool, bool], Tuple[str, dict | None]], redo: bool, is_service: bool, print_all: bool, summarize: bool, batch_size: int, do_wait: bool, max_workers: int) -> None:
    start_time = time.time()
    updated = 0
    meili_batch = []
    task_ids = []
    handler = handler_cls()

    # We manually control the database connection since we're
    # using temp tables and have to be careful not to close the connection.
    handler.connect()
    handler.create_temp_table()

    bar = tqdm(total=handler.count_num_rows(), disable=is_service, leave=True, desc=handler.name, smoothing=0.01)

    while True:
        if print_all:
            _do_print('-----> Fetching more data...', is_service=is_service)
        rows = handler.get_rows_in_batches(batch_size=batch_size)
        if not len(rows):
            break
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_row_func, handler, row, redo, summarize) for row in rows]
            for future in concurrent.futures.as_completed(futures):
                console_identifier, meili_document = future.result()
                if meili_document is not None:
                    if is_service:
                        string = f'{handler.name} --- {console_identifier}'
                    else:
                        string = console_identifier
                    _do_print(string, is_service=is_service)
                    meili_batch.append(meili_document)
                    updated += 1
                bar.set_postfix({'updated': updated})
                bar.update(1)

        if len(meili_batch):
            i = 0
            while True:
                _do_print(f'-----> Inserting {len(meili_batch)} documents...', is_service=is_service)
                try:
                    task = MeilisearchClient.index().add_documents(meili_batch)
                    task_ids.append(task.task_uid)
                    if do_wait:
                        task_result = MeilisearchClient.client().get_task(task.task_uid)
                        while task_result.status != 'succeeded':
                            if task_result.status == 'failed':
                                _logger.critical(f'-----> Failed to add to Meilisearch: {task_result}')
                                sys.exit(1)
                            time.sleep(1)
                            task_result = MeilisearchClient.client().get_task(task.task_uid)
                    break
                except:
                    if i == 3:
                        _logger.critical(f'Exception adding documents: {traceback.format_exc()}')
                        sys.exit(1)
                    _logger.error(f'Failed to add documents (will retry): {traceback.format_exc()}')
                    time.sleep(30)
                    i += 1

        # Reset the batch.
        meili_batch = []

    handler.close()
    bar.close()

    # Reverse the IDs so that we start with the oldest ones first which should be completed by now.
    task_ids.reverse()

    _do_print('-----> Waiting for Meilisearch tasks to complete...', is_service=is_service)
    for task_id in tqdm(task_ids, desc='Processing tasks'):
        task_result = None
        for i in range(10):
            try:
                task_result = get_meilisearch_task_with_retries(task_id)
                break
            except Exception as e:
                _logger.error(f'Exception while waiting for task ID {task_id}: {e}')
                time.sleep(10)
        while not task_result or task_result.status != 'succeeded':  # Can be None if there was an exception in get_meilisearch_task_with_retries()
            if task_result.status == 'failed':
                _logger.critical(f'-----> Failed to add to Meilisearch: {task_result}')
                sys.exit(1)
            time.sleep(1)
            task_result = get_meilisearch_task_with_retries(task_id)

    end_time = time.time()
    execution_time = end_time - start_time
    hours, remainder = divmod(execution_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    _logger.info(f'{handler.name} Run Time: {int(hours)} hours, {int(minutes)} minutes, {int(seconds)} seconds')

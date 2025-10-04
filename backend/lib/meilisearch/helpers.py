import logging
import time

from meilisearch.models.task import Task

from lib.meilisearch.client import MeilisearchClient

_LOGGER = logging.getLogger('MEILISEARCH').getChild('HELPERS')


def get_meilisearch_task_with_retries(task_id: int, max_retries: int = 10, retry_delay: int = 10) -> Task | None:
    for i in range(max_retries):
        try:
            return MeilisearchClient.client().get_task(task_id)
        except Exception as e:
            _LOGGER.error(f'Exception while waiting for task ID {task_id}: {e}')
            if i == max_retries - 1:
                raise
            time.sleep(retry_delay)
            return None
    return None

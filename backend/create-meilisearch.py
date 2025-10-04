import argparse
import time

from lib.config import GLOBAL_SEARCH_INDEX
from lib.meilisearch.client import MeilisearchClient
from lib.meilisearch.consts import MEILISEARCH_HOST, MEILISEARCH_MASTER_KEY
from lib.search.keywords import search_keywords


def main(args):
    MeilisearchClient.initialise(MEILISEARCH_HOST, GLOBAL_SEARCH_INDEX, MEILISEARCH_MASTER_KEY)

    if args.delete_and_recreate_confirm:
        ask = input('Really delete? y/n ')
        if ask != 'y':
            print('Not doing anything...')
            quit(1)

        task = MeilisearchClient.client().delete_index(GLOBAL_SEARCH_INDEX)
        task_status = MeilisearchClient.client().get_task(task.task_uid)
        while task_status.status != 'succeeded':
            if task_status.error and task_status.error['code'] == 'index_not_found':
                break
            print(task_status)
            time.sleep(1)
            task_status = MeilisearchClient.client().get_task(task.task_uid)

        task = MeilisearchClient.client().create_index(GLOBAL_SEARCH_INDEX, {'primaryKey': 'doc_id'})
        task_status = MeilisearchClient.client().get_task(task.task_uid)
        while task_status.status != 'succeeded':
            print(task_status)
            time.sleep(1)
            task_status = MeilisearchClient.client().get_task(task.task_uid)

    index = MeilisearchClient.client().get_index(GLOBAL_SEARCH_INDEX)

    index.update_distinct_attribute('doc_id')

    index.update_searchable_attributes([
        'name',
        'scenario',
        'first_mes',
        'description',
        'mes_example',
        'personality',
        'creator_notes',
        'system_prompt',
        'world_scenario',
        'example_dialogue',
        'post_history_instructions',
        'platform_summary',
        'author',
        'tagline',
        'tags'
    ])

    keyword_list = set()
    keyword_dict = search_keywords()
    for k, v in keyword_dict.items():
        for x in v:
            if isinstance(x, dict):
                name = x['name']
                if name.startswith('chub_'):
                    name = 'chub.' + name
                keyword_list.add(name)
            else:
                keyword_list.add(x)
    keyword_list = list(keyword_list)

    index.update_filterable_attributes(keyword_list)
    index.update_sortable_attributes(keyword_list)

    index.update_ranking_rules([
        'words',
        'typo',
        'proximity',
        'attribute',
        'sort',
        'exactness'
    ])

    index.update_faceting_settings({'maxValuesPerFacet': 100000000})
    index.update_pagination_settings({'maxTotalHits': 100000000})

    index.update_embedders({
        'default': {
            'source': 'userProvided',
            'dimensions': 384
        }
    })

    # If this is None, then it is reprocessing everything because the embedder changed.
    assert index.get_embedders()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--delete-and-recreate-confirm', action='store_true', help='Delete and recreate the index. If not provided, only update fields and config.')
    args = parser.parse_args()

    main(args)

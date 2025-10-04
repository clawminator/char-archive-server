#!/usr/bin/env python3
import argparse
import logging
import signal
import traceback
from multiprocessing import cpu_count

from lib.config import GLOBAL_SEARCH_INDEX
from lib.database.connection import Database
from lib.meilisearch.client import MeilisearchClient
from lib.meilisearch.consts import MEILISEARCH_HOST, MEILISEARCH_MASTER_KEY
from lib.search.handlers.booru import BooruElasticHandler
from lib.search.handlers.char_tavern import CharTavernElasticHandler
from lib.search.handlers.chub_character import ChubCharacterElasticHandler
from lib.search.handlers.chub_lorebook import ChubLorebookElasticHandler
from lib.search.handlers.generic import GenericElasticHandler
from lib.search.handlers.nyaime import NyaimeElasticHandler
from lib.search.handlers.risuai import RisuaiElasticHandler
from lib.search.handlers.webring import WebringElasticHandler
from lib.search.process.meilisearch import sync_card_search_meili
from lib.search.sync_elastic import sync_elastic_source
from lib.suicide import watchdog_expired

logging.basicConfig()
_logger = logging.getLogger('MAIN')
_logger.setLevel(logging.INFO)

ELASTIC_SYNC_IS_SERVICE: bool = False


# TODO: use postgresql nofiy: https://notado.substack.com/p/how-notado-syncs-data-from-postgresql

def main(args):
    Database.initialise(minconn=1, maxconn=100, host='172.0.3.101' if args.remote else '127.0.0.1', database='char_archive', user='char_archive', password='hei3ucheet5oochohjongeisahV3mei0')

    try:
        MeilisearchClient.connect(MEILISEARCH_HOST)
        MeilisearchClient.initialise(MEILISEARCH_HOST, GLOBAL_SEARCH_INDEX, MEILISEARCH_MASTER_KEY, timeout=120)
    except:
        _logger.error(f'Failed to start Meilisearch: {traceback.format_exc()}')
        quit(1)

    # Lower query size if we're connecting remotely.
    batch_size = 100 if not args.remote else 10

    max_workers = cpu_count()
    if args.summary and not args.full_workers:
        max_workers = 1
    _logger.info(f'Using {max_workers} workers')

    _logger.info('Syncing Chub characters...')
    sync_elastic_source(ChubCharacterElasticHandler, process_row_func=sync_card_search_meili, redo=args.redo, is_service=args.service, print_all=args.print_all, summarize=args.summary, batch_size=batch_size, do_wait=args.wait, max_workers=max_workers)
    _logger.info('Syncing Booru characters...')
    sync_elastic_source(BooruElasticHandler, process_row_func=sync_card_search_meili, redo=args.redo, is_service=args.service, print_all=args.print_all, summarize=args.summary, batch_size=batch_size, do_wait=args.wait, max_workers=max_workers)
    _logger.info('Syncing Generic characters...')
    sync_elastic_source(GenericElasticHandler, process_row_func=sync_card_search_meili, redo=args.redo, is_service=args.service, print_all=args.print_all, summarize=args.summary, batch_size=batch_size, do_wait=args.wait, max_workers=max_workers)
    _logger.info('Syncing Nyaime characters...')
    sync_elastic_source(NyaimeElasticHandler, process_row_func=sync_card_search_meili, redo=args.redo, is_service=args.service, print_all=args.print_all, summarize=args.summary, batch_size=batch_size, do_wait=args.wait, max_workers=max_workers)
    _logger.info('Syncing Risuai characters...')
    sync_elastic_source(RisuaiElasticHandler, process_row_func=sync_card_search_meili, redo=args.redo, is_service=args.service, print_all=args.print_all, summarize=args.summary, batch_size=batch_size, do_wait=args.wait, max_workers=max_workers)
    _logger.info('Syncing Webring characters...')
    sync_elastic_source(WebringElasticHandler, process_row_func=sync_card_search_meili, redo=args.redo, is_service=args.service, print_all=args.print_all, summarize=args.summary, batch_size=batch_size, do_wait=args.wait, max_workers=max_workers)
    _logger.info('Syncing Character Tavern Characters...')
    sync_elastic_source(CharTavernElasticHandler, process_row_func=sync_card_search_meili, redo=args.redo, is_service=args.service, print_all=args.print_all, summarize=args.summary, batch_size=batch_size, do_wait=args.wait, max_workers=max_workers)
    _logger.info('Syncing Chub lorebooks...')
    sync_elastic_source(ChubLorebookElasticHandler, process_row_func=sync_card_search_meili, redo=args.redo, is_service=args.service, print_all=args.print_all, summarize=args.summary, batch_size=batch_size, do_wait=args.wait, max_workers=max_workers)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--remote', action='store_true', help='Connect to the Elasticsearch server remotely.')
    parser.add_argument('-s', '--service', action='store_true', help='Run as a service.')
    parser.add_argument('--redo', action='store_true', help='Ignore existing data in Elastic. Existing data will be updated.')
    parser.add_argument('--print-all', action='store_true', help='Print all items as they are processed. By default, only updated items are printed.')
    parser.add_argument('--summary', action='store_true', help='Use Beepo-22B to summarize for embedding.')
    parser.add_argument('--wait', action='store_true', help='Wait for the batch inserts to complete before continuing.')
    parser.add_argument('--full-workers', action='store_true', help="Don't limit worker count.")
    parser.add_argument('--run-time-limit', type=int, default=7200, help='If the program runs longer than this, kill it. Value in seconds. Set to `-1` to disable. Default: 7200 (2 hours)')

    args = parser.parse_args()

    if args.run_time_limit == -1:
        _logger.info(f'Run time limit disabled.')
    else:
        _logger.info(f'Run time limit: {args.run_time_limit} seconds.')
        signal.alarm(args.run_time_limit)
        signal.signal(signal.SIGALRM, watchdog_expired)

    main(args)

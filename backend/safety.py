#!/usr/bin/env python3
import argparse
import json
import logging
import re
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple

import openai
from func_timeout import FunctionTimedOut, func_set_timeout
from openai import OpenAI
from pydantic import BaseModel
from tqdm import tqdm

from lib.database.connection import Database
from lib.moderation import ModerationCategories, BadShit, ModerationResult
from lib.safety.handlers.booru import BooruSafetyHandler
from lib.safety.handlers.char_tavern import CharTavernSafetyHandler
from lib.safety.handlers.chub import ChubSafetyHandler
from lib.safety.handlers.chub_lore import ChubLoreSafetyHandler
from lib.safety.handlers.generic import GenericSafetyHandler
from lib.safety.handlers.nyaime import NyaimeSafetyHandler
from lib.safety.handlers.risuai import RisuaiSafetyHandler
from lib.safety.handlers.safety_handler import SafetyHandler
from lib.safety.handlers.webring import WebringSafetyHandler

logging.basicConfig()
logger = logging.getLogger('MAIN')
logger.setLevel(logging.INFO)


class SqlStatement(BaseModel):
    table_name: str
    postfix: str


API_KEYS = ['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', 'sk-proj-yv0YqakSy0sqNPAmLO1iT3BlbkFJzpzZtr86g1DmuLAGdgWX', 'sk-proj-i0NJHs8gFsalcTcsy3xnT3BlbkFJCt470zVHGJF7cwyk8GWl']

IS_SERVICE: bool = False
DISABLE_AI: bool = False


class ApiKeyManager:
    def __init__(self, keys):
        self.keys = keys
        self.current_index = 0

    def get_key(self):
        key = self.keys[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.keys)
        return key


manager = ApiKeyManager(API_KEYS)


def manual_check(text: str):
    is_hidden = re.search(r'allthefallen', text, re.IGNORECASE) is not None
    return BadShit(
        loli=re.search(r'\b(loli|underage|preteen|cunny|shota|daughter)\b', text, re.IGNORECASE) is not None,
    ), is_hidden


@func_set_timeout(60)
def do_moderation(text: str, key: str) -> Tuple[dict, bool]:
    assert isinstance(text, str)
    client = OpenAI(api_key=key)
    while True:
        try:
            bad_shit, is_hidden = manual_check(text)
            if not DISABLE_AI:
                detected_categories = client.moderations.create(input=text).results[0].categories.model_dump()
            else:
                detected_categories = ModerationCategories(sexual=None, hate=None, harassment=None, self_harm=None, sexual_minors=None, hate_threatening=None, violence_graphic=None, self_harm_intent=None, self_harm_instructions=None, harassment_threatening=None, violence=None)
            return ModerationResult(categories=detected_categories, bad_shit=bad_shit).model_dump(), is_hidden
        except openai.RateLimitError as e:
            msg = e.message
        except openai.InternalServerError:
            msg = 'OpenAI Internal Server Error'
        if IS_SERVICE:
            logger.info(msg)
        else:
            tqdm.write(f'ERROR: {msg}')
        time.sleep(5)


def moderation_with_timeout(text: str, key: str):
    for _ in range(3):
        try:
            return do_moderation(text, key)
        except FunctionTimedOut:
            logger.warning('Moderation timed out...')
            time.sleep(10)
    logger.error('Moderation timed out!')
    time.sleep(120)


def process_row(handler, tqdm_card_name, row):
    key = manager.get_key() if not DISABLE_AI else 'abc'
    card_text = json.dumps(row['definition'])
    moderation_result, is_hidden = moderation_with_timeout(card_text, key)

    existing_metadata = row['metadata']
    if existing_metadata.get('safety') is None:
        existing_metadata['safety'] = {}
    new_metadata = existing_metadata.copy()
    new_metadata['safety'] = moderation_result
    handler.update_metadata(new_metadata, row)
    if is_hidden:
        handler.set_hidden()

    return tqdm_card_name


def process(handler: SafetyHandler):
    total_rows = handler.total_card_rows()
    pbar = tqdm(total=total_rows, disable=IS_SERVICE, desc=handler.tqdm_desc, leave=True)

    with ThreadPoolExecutor() as executor:
        while True:
            rows = handler.iterate_rows()
            if not rows:
                break  # No more rows to process

            futures = []
            for row in rows:
                future = executor.submit(process_row, handler, handler.name_format.format(**row), row)
                futures.append(future)

            for future in futures:
                try:
                    name = future.result()
                    if IS_SERVICE:
                        logger.info(name)
                    else:
                        tqdm.write(name)
                    pbar.update(1)
                except Exception as e:
                    logger.error(f"Error processing row: {e}")
                    pbar.update(1)

    pbar.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--remote', action='store_true', help='Connect to the server remotely.')
    parser.add_argument('-s', '--service', action='store_true', help='Run as a service.')
    parser.add_argument('--reprocess', action='store_true', help='Force reprocessing of all data.')
    parser.add_argument('--no-ai', action='store_true', help='Disable all AI features.')
    args = parser.parse_args()

    Database.initialise(minconn=1, maxconn=100, host='172.0.3.101' if args.remote else '127.0.0.1', database='char_archive', user='char_archive', password='hei3ucheet5oochohjongeisahV3mei0')

    IS_SERVICE = args.service
    DISABLE_AI = args.no_ai

    logger.info('Processing chub...')
    process(ChubSafetyHandler(reprocess=args.reprocess))
    logger.info('Processing generic...')
    process(GenericSafetyHandler(reprocess=args.reprocess))
    logger.info('Processing risuai...')
    process(RisuaiSafetyHandler(reprocess=args.reprocess))
    logger.info('Processing nyaime...')
    process(NyaimeSafetyHandler(reprocess=args.reprocess))
    logger.info('Processing booru...')
    process(BooruSafetyHandler(reprocess=args.reprocess))
    logger.info('Processing webring...')
    process(WebringSafetyHandler(reprocess=args.reprocess))
    logger.info('Processing char tavern...')
    process(CharTavernSafetyHandler(reprocess=args.reprocess))
    logger.info('Processing chub lorebooks...')
    process(ChubLoreSafetyHandler(reprocess=args.reprocess))

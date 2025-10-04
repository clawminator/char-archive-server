#!/usr/bin/env python3
import argparse
import logging
import re
import sys
import threading
import time
import traceback
from queue import Queue

from func_timeout import func_set_timeout, FunctionTimedOut
from openai import OpenAI
from psycopg2.extras import RealDictCursor
from tqdm import tqdm

from lib.database.connection import Database, CursorFromConnectionFromPool

logging.basicConfig()
logger = logging.getLogger('MAIN')
logger.setLevel(logging.INFO)

CHAR_RE = re.compile(r'{{char}}', re.IGNORECASE)

PRINT_LOCK = threading.Lock()

client = OpenAI(
    api_key='sk-yFoNK2hEItEKcrifXf31dw',
    base_url='https://llm.example.com/v1',
)

WORKER_COUNT = 1
MAX_CHARS = 5000


def trim_incomplete_sentences(text: str):
    last_period_index = text.rfind(".")
    if last_period_index == -1:
        return ""
    else:
        return text[:last_period_index + 1]


def prepare_ai_response(text: str):
    text = text.replace('\n\n', '\n').replace('### Response:\n', '')
    text = re.sub('<[^<]+?>', '', text)  # Remove HTML tags
    text = trim_incomplete_sentences(text.strip(' ').strip('\n')).strip('*')
    # parts = text.split('\n')
    return text


def fetch_data(table_name, redo: bool, test: bool, pkey_column: str):
    sql = f"SELECT * FROM {table_name}"
    if not redo:
        sql += " WHERE summary = '' OR summary IS NULL"
    if test:
        sql += " LIMIT 10"
    sql += f" ORDER BY {pkey_column} ASC"
    with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(sql)
        return cursor.fetchall()


def prepare_msg(text: str):
    specials = [('\n', '\\n'), ('\r', '\\r'), ('\t', '\\t')]
    for special in specials:
        text = text.replace(special[0], special[1])
    text = text.replace('<BOT>', '{{char}}')
    text = text.replace('<USER>', '{{user}}')
    return text


@func_set_timeout(60)
def process_row(row, table_name, is_service, pbar: tqdm, pkey_column: str):
    item_str = f"{row['name']} -- {row[pkey_column]}"
    description = trim_incomplete_sentences(re.sub(CHAR_RE, prepare_msg(row['name']), prepare_msg(row['definition']['data']['description']))[:MAX_CHARS])
    first_mes = trim_incomplete_sentences(re.sub(CHAR_RE, prepare_msg(row['name']), prepare_msg(row['definition']['data']['first_mes']))[:MAX_CHARS])
    info = f"""{row['name']}\n\n{description}\n\n{first_mes}"""
    msg = f"""You are to write a summary of the following role-play scenario to be used to generate a text embedding for a vector search database. Write no more than one paragraph of any length. Describe the characters and scenario accurately and make sure to not leave out any info. You are not a participant in the role-play, nor a character.\n\n### Scenario:\n{info}\n\n\n### Response: """

    response = None
    for i in range(10):
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": msg,
                    }
                ],
                model="Beepo-22B",
                max_tokens=300,
                seed=1,
                user='char-archive-summary'
            )
            response = prepare_ai_response(chat_completion.choices[0].message.content)
            break
        except Exception as e:
            last_traceback = traceback.format_exc()
            log_msg = f'Failed to generate for "{item_str}": {e}'
            if is_service:
                logger.warning(log_msg)
            else:
                with PRINT_LOCK:
                    pbar.write(log_msg)
            time.sleep(10)
        if not response:
            logger.critical(f'Exception generating for "{item_str}": {last_traceback}')
            sys.exit(1)

    with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(f'UPDATE {table_name} SET summary = %s WHERE {pkey_column} = %s', (response, row[pkey_column]))

    # Tagline is sometimes text from the website's frontend. But if there was no such text, fill in the tagline from the card's def.
    if row['tagline'] is None:
        scenario = re.sub(CHAR_RE, row['name'], row['definition']['data']['scenario'])
        with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(f'UPDATE {table_name} SET tagline = %s WHERE {pkey_column} = %s', (scenario, row[pkey_column]))

    if is_service:
        logger.info(item_str)
    else:
        with PRINT_LOCK:
            pbar.write(item_str)

    with PRINT_LOCK:
        pbar.update(1)


def worker():
    while True:
        item = q.get()
        if item is None:
            return
        for _ in range(3):
            try:
                process_row(*item)
                break
            except FunctionTimedOut:
                continue
        q.task_done()


def process_rows(rows, table_name, is_service, pkey_column):
    pbar = tqdm(total=len(rows), disable=is_service, desc=table_name)
    for row in rows:
        q.put((row, table_name, is_service, pbar, pkey_column))

    q.join()  # Block until all tasks are done
    pbar.close()
    msg = f'{table_name} done...'
    if is_service:
        logger.info(msg)
    else:
        with PRINT_LOCK:
            pbar.write(msg)


def main(args):
    Database.initialise(minconn=1, maxconn=100, host='172.0.3.101' if args.remote else '127.0.0.1', database='char_archive', user='char_archive', password='hei3ucheet5oochohjongeisahV3mei0')
    generic_rows = fetch_data('generic_character_def', args.redo, args.test, 'card_data_hash')
    process_rows(generic_rows, 'generic_character_def', args.service, 'card_data_hash')
    booru_rows = fetch_data('booru_character_def', args.redo, args.test, 'id')
    process_rows(booru_rows, 'booru_character_def', args.service, 'id')
    webring_rows = fetch_data('webring_character_def', args.redo, args.test, 'card_data_hash')
    process_rows(webring_rows, 'webring_character_def', args.service, 'card_data_hash')

    logger.info('Ending...')

    # Stop workers
    for i in range(WORKER_COUNT):
        q.put(None)
    for t in threads:
        t.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--remote', action='store_true', help='Connect to the server remotely.')
    parser.add_argument('-s', '--service', action='store_true', help='Run as a service.')
    parser.add_argument('--redo', action='store_true', help='Redo all summaries.')
    parser.add_argument('--test', action='store_true')
    args = parser.parse_args()

    q = Queue()
    threads = []
    for i in range(WORKER_COUNT):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    main(args)

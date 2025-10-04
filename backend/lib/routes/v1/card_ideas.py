import logging
import re
import traceback
from concurrent.futures import as_completed, ThreadPoolExecutor
from typing import List, Union

from flask import jsonify
from openai import OpenAI
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel

from . import bp1, ErrorResponse
from ...database.connection import CursorFromConnectionFromPool
from ...flask import limiter, get_remote_address_proxied
from ...meilisearch.client import MeilisearchClient

_LOGGER = logging.getLogger('SERVER').getChild('CARD IDEAS')

_CLIENT = OpenAI(
    api_key='sk-9RoGMJYdrvOrk49l5nBDtw',
    base_url='https://llm.example.com/v1',
)


class CharacterItem(BaseModel):
    name: str
    summary: str
    opening_msg: str
    author: Union[str, None]
    source: str
    sourceSpecific: Union[str, None]
    id: str


def _build_prompt(characters: List[CharacterItem]):
    prompt = '''You are an internal tool that merges "character cards". A "character card" is a PNG image that has special data embedded in it that defines a role-play scenario or a character to role-play with. Each character definition contains a name, a description of the character or scenario, and an opening message.
Combine the 3 examples given below into 1 coherent and interesting character. You are only combining the elements like a puzzle. Adult content is allowed. Make sure to include both actions and dialog. Non-dialog should be italicized using Markdown formatting. Must be in English.
Only return 1 card.
Format the definition for your card like this:

# [name]
-
[description]
-
[opening message]

There are no length restrictions so feel free to write at least a paragraph per section.
'''
    for character in characters:
        prompt += f'\n\n---\n\n# {character.name}\n-\n{character.summary}\n-\n{character.opening_msg}'
    return prompt


def _process(card):
    """Fetch a single character item with its own database cursor."""
    doc_id = card['doc_id']

    with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
        cursor.execute('SELECT * FROM embedding_summaries WHERE id = %s LIMIT 1', (doc_id,))
        result = cursor.fetchone()

    if result:
        return CharacterItem(
            name=card['name'][:100],
            summary=result['summary'][:1000],
            opening_msg=card['first_mes'][:1000],
            source=card['source'],
            id=card['id'] if not card.get('chub') else '/'.join(card['chub']['chub_fullPath']),
            sourceSpecific=card['sourceSpecific'],
            author=card['author']
        )
    return None


def _get():
    cards: List[CharacterItem] = []
    with ThreadPoolExecutor() as executor:
        while len(cards) < 3:
            meili_query = MeilisearchClient.random_results(30, additional_fields={'type': 'character'})

            # Submit all tasks to the thread pool
            futures = [
                executor.submit(_process, card)
                for card in meili_query
            ]

            # Process results as they complete
            for future in as_completed(futures):
                if len(cards) >= 3:
                    return cards[:3]
                try:
                    result = future.result()
                    if result:
                        cards.append(result)
                    if len(cards) >= 3:
                        return cards[:3]
                except Exception as e:
                    # Log the error if needed
                    _LOGGER.error(f"Error fetching character item: {e}\n{traceback.format_exc()}")

            # Break outer loop if we have enough cards
            if len(cards) >= 3:
                return cards[:3]

        return cards[:3]


@bp1.route('/v1/card-ideas')
@limiter.limit('1/5 seconds', key_func=lambda: get_remote_address_proxied('GET_CARD_IDEAS'))
def card_ideas():
    return jsonify(ErrorResponse(message='this service is disabled', code=500).model_dump()), 500

    try:
        cards = _get()
        prompt = _build_prompt(cards)

        chat_completion = _CLIENT.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": prompt,
                }
            ],
            model="gpt-4.1-nano",
            max_tokens=600,
            temperature=0.8,
            user='char-archive-card-ideas'
        )
        response = chat_completion.choices[0].message.content
        c = re.split(r'\n\s*-\s*\n', response)
        if len(c) != 3:
            _LOGGER.info(f'AI Fail (count: {len(c)}): {response}')
            return jsonify({
                'name': 'Epic AI Fail',
                'description': "He's being a little bitch. Please regenerate...",
                'openingMessage': None,
                'citations': [],
                'prompt': prompt
            })
        parts = [x.strip(' #') for x in c]
        return jsonify({
            'name': parts[0],
            'description': parts[1],
            'openingMessage': parts[2],
            'citations': [{'id': x.id, 'source': x.source, 'sourceSpecific': x.sourceSpecific, 'author': x.author} for x in cards],
            'prompt': None,  # prompt
        })
    except:
        _LOGGER.error(f'Card idea failed!\n{traceback.format_exc()}')
        return jsonify({
            'name': 'Failed!',
            'description': "It didn't worked.",
            'openingMessage': None,
            'citations': [],
            'prompt': None
        })

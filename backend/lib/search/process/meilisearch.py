import json
import logging
import sys
import time
import traceback
from typing import Tuple

from meilisearch.errors import MeilisearchApiError
from openai import OpenAI
from sentence_transformers import SentenceTransformer

from lib.meilisearch.client import MeilisearchClient
from lib.search.empty_embedding import EMPTY_EMBEDDING_VECTOR
from lib.search.handlers.base import ElasticHandler
from summarization import prepare_ai_response, prepare_msg, trim_incomplete_sentences

_logger = logging.getLogger('PROCESSSEARCH')

_model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')

_client = OpenAI(
    api_key='sk-yFoNK2hEItEKcrifXf31dw',
    base_url='https://llm.example.com/v1',
)


# TODO: add an option to generate an embedding from a large, high-quality model running on goblin. This should be done once everything has been summarized. If the option is not set, fall back to the small embedding.
# https://huggingface.co/BAAI/bge-large-en-v1.5
# https://huggingface.co/nvidia/NV-Embed-v2
# https://ragaboutit.com/deploying-nvidia-nv-embed-v2-models-in-production-a-comprehensive-guide/

def sync_card_search_meili(handler: ElasticHandler, row, redo: bool, summarize: bool) -> Tuple[str, dict | None]:
    i = 0
    while True:
        try:
            item_handler = handler.handler_cls(row)
            item_handler.fetch_more_data()
            summary_exists = False
            new_summary = False

            if redo or not MeilisearchClient.doc_exists(item_handler.doc_id()):
                try:
                    generated_doc = item_handler.create_item()
                except Exception as e:
                    _logger.critical(f'Failed to build document for "{item_handler.console_identifier()}": {e}\n{traceback.format_exc()}')
                    return item_handler.console_identifier(), None

                if not generated_doc:
                    # Will return None if no safety yet.
                    return item_handler.console_identifier(), None

                if summarize:
                    try:
                        doc_data = MeilisearchClient.index().get_document(item_handler.doc_id())
                    except MeilisearchApiError as e:
                        if 'not found' in e.message:
                            doc_data = None
                        else:
                            raise

                    if not doc_data:
                        is_empty_embedding = True
                    else:
                        doc_data_dict = dict(doc_data)['_Document__doc']
                        is_empty_embedding = doc_data_dict.get('_vectors', {}).get('embedder') == EMPTY_EMBEDDING_VECTOR
                        del doc_data_dict
                    del doc_data

                    # Only summarize items that have a dummy embedding.
                    if not redo and not is_empty_embedding:
                        return item_handler.console_identifier(), None

                    existing_summary = handler.get_summary(item_handler.doc_id())
                    if existing_summary:
                        output_text = existing_summary
                        summary_exists = True
                    else:
                        text = generated_doc.get_text_for_embedding()
                        output_text = _summarize_for_embedding(text, handler.name)
                        handler.save_summary(item_handler.doc_id(), output_text)
                        new_summary = True
                    embedding = _model.encode(output_text).tolist()
                else:
                    existing_summary = handler.get_summary(item_handler.doc_id())
                    if existing_summary:
                        embedding = _model.encode(existing_summary).tolist()
                        summary_exists = True
                    else:
                        embedding = EMPTY_EMBEDDING_VECTOR

                generated_doc.embedding = embedding

                meili_document = json.loads(generated_doc.model_dump_json())
                meili_document['_vectors'] = {
                    'default': meili_document.pop('embedding')
                }

                summary_text = ''
                if summary_exists:
                    summary_text = ' (summary exists)'
                elif new_summary:
                    summary_text = ' (new summary)'

                output_text = item_handler.console_identifier() + summary_text
                return output_text, meili_document
            return item_handler.console_identifier(), None
        except:
            if i == 3:
                _logger.critical(f'Exception building document: {traceback.format_exc()}')
                sys.exit(1)
            _logger.error(f'Failed to build document (will retry): {traceback.format_exc()}')
            time.sleep(30)
            i += 1


def _summarize_for_embedding(text: str, item_str: str):
    msg = f"""You are to write a summary of the following role-play scenario to be used to generate a text embedding for a vector search database. Write no more than one paragraph of any length. Describe the characters and scenario accurately and make sure to not leave out any info. You are not a participant in the role-play, nor a character. Don't start your summary with something like "In this role-play".\n\n### Scenario:\n{trim_incomplete_sentences(prepare_msg(text[:5000]))}\n\n\n### Response: """
    response = None
    last_traceback = None
    for i in range(10):
        try:
            chat_completion = _client.chat.completions.create(
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
            log_msg = f'Failed to generate for "{item_str}" (will retry): {e}'
            _logger.warning(log_msg)
            time.sleep(60)
        if not response:
            _logger.critical(f'Exception generating for "{item_str}": {last_traceback}')
            sys.exit(1)
    return response.strip('"').strip("'")

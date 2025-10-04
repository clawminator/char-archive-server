from lib.search.search_item import SearchChar
from lib.search.handlers.base import ElasticHandler, ElasticItemHandler
from lib.sources import Sources


class GenericElasticHandler(ElasticHandler):
    def __init__(self):
        super().__init__('Generic', 'generic_character_def', 'card_data_hash', GenericElasticItemHandler)


class GenericElasticItemHandler(ElasticItemHandler):
    def __init__(self, data: dict):
        super().__init__(data)

    def _generate_doc_id(self) -> str:
        return f'generic{self._node_row["name"]}{self._node_row["card_data_hash"]}character'

    def console_identifier(self):
        return f'{self._node_row["name"]} -- {self._node_row["card_data_hash"]}'

    def _do_create_item(self):
        return SearchChar(
            name=self._node_row['name'],
            source=Sources.generic.value,
            sourceSpecific=self._node_row["source"],
            scenario=self._node_row['definition']['data']['scenario'],
            first_mes=self._node_row['definition']['data']['scenario'],
            description=self._node_row['definition']['data']['description'],
            mes_example=self._node_row['definition']['data']['mes_example'],
            personality=self._node_row['definition']['data']['personality'],
            creator_notes=self._node_row['definition']['data']['creator_notes'],
            system_prompt=self._node_row['definition']['data']['system_prompt'],
            world_scenario=self._node_row['definition']['data']['world_scenario'],
            example_dialogue=self._node_row['definition']['data']['example_dialogue'],
            alternate_greetings=self._node_row['definition']['data']['alternate_greetings'],
            post_history_instructions=self._node_row['definition']['data']['post_history_instructions'],
            created=self._node_row['definition']['create_date'],
            updated=self._node_row['added'],
            added=self._node_row['added'],
            image_hash=self._node_row['image_hash'],
            platform_summary=self._node_row['summary'],
            author=self._node_row['definition']['data']['creator'],
            id=str(self._node_row['card_data_hash']),
            tagline=self._node_row['tagline'],
            tags=self._node_row['definition']['data']['tags'],
            safety=self._node_row['metadata'].get('safety', {}),
            downloads=None,
            source_url=self._node_row['source_url'],
            embedding=[],
            token_count=self._node_row['metadata']['totalTokens'],
            doc_id=self.doc_id()
        )

from lib.search.handlers.chub import ChubSearchNode
from lib.search.search_item import SearchChar, SearchLore
from lib.sources import SOURCES_VALUES, SOURCES_SPECIFIC_VALUES


def search_keywords():
    return {
        'character': list([{'name': k, 'desc': v.description} for k, v in SearchChar.model_fields.items() if k != 'chub' and v.description is not None]),
        'lorebook': list([{'name': k, 'desc': v.description} for k, v in SearchLore.model_fields.items() if k != 'chub' and k != 'lore_content' and v.description is not None]),
        'chub': list([{'name': k, 'desc': v.description} for k, v in ChubSearchNode.model_fields.items() if k.startswith('chub_')]),
        'sources': {
            'types': SOURCES_VALUES,
            'specific': SOURCES_SPECIFIC_VALUES
        },
    }

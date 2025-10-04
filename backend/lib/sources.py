from enum import Enum


class Sources(str, Enum):
    chub = 'chub'
    generic = 'generic'
    booru = 'booru'
    catbox = 'catbox'
    roko = 'roko'
    venusai = 'venusai'
    janitorai = 'janitorai'
    nyaime = 'nyaime'
    risuai = 'risuai'
    webring = 'webring'
    char_tavern = 'char-tavern'


SOURCES_SPECIFIC_VALUES = [Sources.generic.value, Sources.catbox.value, Sources.roko.value, Sources.venusai.value, Sources.janitorai.value]
SOURCES_VALUES = [e.value for e in Sources.__members__.values() if e.value not in SOURCES_SPECIFIC_VALUES]

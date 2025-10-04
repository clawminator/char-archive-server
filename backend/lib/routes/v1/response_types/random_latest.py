from datetime import timezone, datetime
from typing import Optional, Union, Tuple

from dateutil.parser import parse
from pydantic import BaseModel, field_validator

from lib.sources import Sources


class RandomOrLatestResponseItem(BaseModel):
    source: Sources
    name: str
    type: Optional[str] = 'character'  # Will always be a character
    added: Optional[str]
    id: Union[int, str]
    author: Optional[str] = None
    tagline: Optional[str] = ''

    @field_validator('added', mode='before')
    @classmethod
    def parse_date(cls, v):
        if isinstance(v, str):
            v = parse(v)
        elif isinstance(v, (int, float)):
            v = datetime.fromtimestamp(v)
        return v.astimezone(timezone.utc).isoformat()

    @field_validator('type', mode='before')
    @classmethod
    def force_char(cls, v):
        # Allow us to just slam the database row into a model.
        return 'character'


class BooruRandomOrLatestResponseItem(RandomOrLatestResponseItem):
    source: str = Sources.booru.value


class ChubInfo(BaseModel):
    fullPath: Tuple[str, str]


class ChubRandomOrLatestResponseItem(RandomOrLatestResponseItem):
    chub: ChubInfo
    source: str = Sources.chub.value


class GenericRandomOrLatestResponseItem(RandomOrLatestResponseItem):
    sourceSpecific: str
    source: str = Sources.generic.value


class NyaimeRandomOrLatestResponseItem(RandomOrLatestResponseItem):
    source: str = Sources.nyaime.value


class RisuaiRandomOrLatestResponseItem(RandomOrLatestResponseItem):
    source: str = Sources.risuai.value


class WebringRandomOrLatestResponseItem(RandomOrLatestResponseItem):
    source: str = Sources.webring.value


class CharTavernRandomOrLatestResponseItem(RandomOrLatestResponseItem):
    source: str = Sources.char_tavern.value

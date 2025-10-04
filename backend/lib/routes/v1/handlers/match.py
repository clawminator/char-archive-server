from typing import Type

from lib.routes.v1.handlers.booru import BooruHandler
from lib.routes.v1.handlers.char_tavern import CharTavernHandler
from lib.routes.v1.handlers.chub import ChubHandler
from lib.routes.v1.handlers.generic import GenericHandler
from lib.routes.v1.handlers.handler import Handler
from lib.routes.v1.handlers.nyaime import NyaimeHandler
from lib.routes.v1.handlers.risuai import RisuaiHandler
from lib.routes.v1.handlers.webring import WebringHandler
from lib.sources import Sources, SOURCES_SPECIFIC_VALUES


def match_handler(site: str) -> Type[Handler] | None:
    if site == Sources.chub.value:
        return ChubHandler
    elif site in SOURCES_SPECIFIC_VALUES:
        return GenericHandler
    elif site == Sources.booru.value:
        return BooruHandler
    elif site == Sources.nyaime.value:
        return NyaimeHandler
    elif site == Sources.risuai.value:
        return RisuaiHandler
    elif site == Sources.webring.value:
        return WebringHandler
    elif site == Sources.char_tavern.value:
        return CharTavernHandler
    else:
        return None

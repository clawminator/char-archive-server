from types import NoneType
from typing import Union

from pydantic import BaseModel


class ModerationCategories(BaseModel):
    sexual: Union[bool, NoneType]
    hate: Union[bool, NoneType]
    harassment: Union[bool, NoneType]
    self_harm: Union[bool, NoneType]
    sexual_minors: Union[bool, NoneType]
    hate_threatening: Union[bool, NoneType]
    violence_graphic: Union[bool, NoneType]
    self_harm_intent: Union[bool, NoneType]
    self_harm_instructions: Union[bool, NoneType]
    harassment_threatening: Union[bool, NoneType]
    violence: Union[bool, NoneType]


class BadShit(BaseModel):
    loli: bool


class ModerationResult(BaseModel):
    bad_shit: BadShit
    categories: ModerationCategories

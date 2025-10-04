from datetime import timezone, datetime
from typing import Union, List, Any, Dict, Tuple, Optional

import markdown
from dateutil.parser import parse
from pydantic import BaseModel, Field, field_validator

from lib.helpers.bleach import sanitize_html
from lib.sources import Sources


class UserAvatar(BaseModel):
    hash: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    error: Optional[str] = None


class UserCardItem(BaseModel):
    id: Union[str, int]
    downloads: Optional[int] = None
    type: str
    path: Optional[Union[Tuple[str, str], Tuple[str, str, str]]] = None
    created: Optional[Union[str, datetime]] = None
    updated: Optional[Union[str, datetime]] = None
    description: Optional[str] = ''
    tagline: str
    name: str
    source: str
    sourceSpecific: Optional[str] = None
    added: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

    @field_validator('created', 'updated', 'added', mode='before')
    @classmethod
    def parse_date(cls, v):
        if isinstance(v, str):
            v = parse(v)
        if isinstance(v, datetime):
            return v.astimezone(timezone.utc).isoformat()
        return v


class UserResponse(BaseModel):
    username: str
    added: Optional[str] = None
    updated: Optional[str] = None
    id: Optional[Union[str, int]] = None
    characters: List[UserCardItem] = Field(default_factory=list)
    lorebooks: List[Any] = Field(default_factory=list)
    source: Sources
    data: Dict[str, Any] = Field(default_factory=dict)
    avatar: UserAvatar
    missing: bool = False
    description: Optional[str] = ''

    @field_validator('added', 'updated', mode='before')
    @classmethod
    def parse_date(cls, v):
        if isinstance(v, str):
            v = parse(v)
        if isinstance(v, datetime):
            return v.astimezone(timezone.utc).isoformat()
        return v

    @field_validator('description', mode='before')
    @classmethod
    def sanitize_fields(cls, v):
        assert isinstance(v, str)
        return sanitize_html(markdown.markdown(v))

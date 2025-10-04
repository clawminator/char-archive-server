from datetime import timezone, datetime
from typing import Optional, List, Dict, Any, Union, Tuple

import markdown
from dateutil.parser import parse
from pydantic import BaseModel, Field, field_validator, Extra

from lib.helpers.bleach import sanitize_html
from lib.sources import Sources


class NodeChat(BaseModel):
    count: int
    created: str

    @field_validator('created')
    @classmethod
    def parse_date(cls, v):
        return parse(v).astimezone(timezone.utc).isoformat()


class NodeRating(BaseModel):
    created: Optional[str] = None
    comment: Optional[str] = ''

    @field_validator('created')
    @classmethod
    def parse_date(cls, v):
        if v:
            return parse(v).astimezone(timezone.utc).isoformat()
        return v

    class Config:
        extra = Extra.allow


class NodeImage(BaseModel):
    error: Optional[str] = None
    height: Union[int, None] = None
    width: Union[int, None] = None


class NodeMetadata(BaseModel):
    # Hardcoded, required fields
    totalTokens: int = -1

    # Allow everything else
    class Config:
        extra = Extra.allow
        # exclude_none = True


class NodeChubForked(BaseModel):
    forked: bool = False
    source: Optional[Tuple[str, str]] = None
    error: Optional[str] = None


class NodeChubForks(BaseModel):
    count: int = 0
    forks: List[Tuple[str, str] | Tuple[str, str, str]] = Field(default_factory=list)


class NodeChub(BaseModel):
    forked: Optional[NodeChubForked] = NodeChubForked()
    forks: Optional[NodeChubForks] = NodeChubForks()
    anonymousAuthor: Optional[str] = None


class NodeResponse(BaseModel):
    name: str
    source: Sources
    image: NodeImage
    added: Union[str, datetime]
    type: str
    metadata: NodeMetadata
    updated: Optional[str] = None
    created: Optional[str] = None
    id: Optional[Union[str, int]] = None
    author: Optional[str] = None
    node: Dict[str, Any] = Field(default_factory=dict)
    chats: Optional[List[NodeChat]] = Field(default_factory=list)
    ratings: Optional[List[NodeRating]] = Field(default_factory=list)
    description: Optional[str] = ''
    tagline: Optional[str] = ''
    creatorNotes: Optional[str] = ''

    # This is a dict such as:
    # {"0": "2025-04-30T00:44:30.941987+00:00"}
    # because we want to emphasize the order of the items, where `0`
    # would refer to the first version.
    versions: Dict[str, Any] = Field(default_factory=dict)

    sourceSpecific: Optional[str] = None
    chub: Optional[NodeChub] = None
    tags: List[str] = Field(default_factory=list)

    @field_validator('added', 'updated', 'created', mode='before')
    @classmethod
    def parse_date(cls, v):
        if isinstance(v, str):
            return parse(v).astimezone(timezone.utc).isoformat()
        elif isinstance(v, datetime):
            return v.astimezone(timezone.utc).isoformat()
        return v

    @field_validator('creatorNotes', 'description', mode='before')
    @classmethod
    def sanitize_fields(cls, v):
        assert isinstance(v, str)
        return sanitize_html(markdown.markdown(v))

    # TODO: why is this here?????
    class Config:
        arbitrary_types_allowed = True

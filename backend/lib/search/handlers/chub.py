from typing import List, Optional

from pydantic import BaseModel, Field


class ChubSearchNode(BaseModel):
    # All fields need to start with `chub_` since the search route key list filters out ones that don't have that.
    chub_fullPath: List[str] = Field(..., description='The "fullPath" of a node. This is the internal chub.ai identifier.')
    chub_fork: bool = Field(False, description='The card is a fork. True/false.')
    chub_anonymousAuthor: Optional[str] = Field(None, description='The de-anonymized author.')

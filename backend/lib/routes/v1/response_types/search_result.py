from datetime import datetime
from typing import Optional, List, Dict, Any, Union

from pydantic import BaseModel

from lib.moderation import ModerationResult


class SearchListingsItem(BaseModel):
    # We don't need strict validation since the Elastic insert script does that for us.
    # This is only to filter fields to reduce network data usage.

    # Common fields from SearchItemBase
    author: Optional[str] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    id: Union[str, int]
    name: str
    source: str  # Sources enum
    sourceSpecific: Optional[str] = None
    tagline: str
    tags: List[str]
    type: str  # 'character' or 'lorebook'
    safety: ModerationResult
    chub: Optional[Dict[str, Any]] = None

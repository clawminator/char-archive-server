import datetime
from enum import Enum
from typing import Optional, List, Union

from pydantic import BaseModel, Field, field_validator, field_serializer, ConfigDict

from lib.sources import Sources


class ItemTypes(str, Enum):
    character = 'character'
    lorebook = 'lorebook'


class SearchItemBase(BaseModel):
    """Base class for search items with common fields"""
    source: Sources = Field(..., description='The source to filter by. Refer to the Sources section below.')
    sourceSpecific: Optional[str] = Field(None, description='The specific source to filter by. Refer to the Specific Sources section below.')
    name: str = Field(..., description='Name of the item.')
    created: Optional[datetime.datetime] = Field(None, description='The timestamp the item was created.')
    updated: Optional[datetime.datetime] = Field(None, description='The timestamp the item was updated.')
    added: datetime.datetime = Field(..., description='The timestamp the item was added to the archive.')
    image_hash: str = Field(..., description='The MD5 hash of the image without any metadata.')
    platform_summary: str = Field(..., description="The summary of the item. For chub.ai, this is the item's description shown on the website.")
    author: Optional[str] = Field('', description='The author of the item.')
    id: Union[str, int] = Field(..., description="The internal ID of the item. For chub.ai, this is the item's ID. For all other items, it's the internal ID.")
    tagline: str = Field(..., description="The item tagline.")
    tags: List[str] = Field(default_factory=list, description="The item tags.")
    type: ItemTypes = Field(..., description='The item type. "character" or "lorebook"')
    downloads: Optional[int] = Field(None, description='The number of downloads for an item.')
    token_count: int = Field(None, description='The number of tokens an item contains.')
    safety: dict  # Should be `ModerationResult` but is left as a dict so that it can be validated manually.
    embedding: list
    doc_id: str

    model_config = ConfigDict()

    @field_validator('created', 'updated', 'added', mode='before')
    @classmethod
    def validate_datetime(cls, v):
        """Set datetime to None if it's before 1990"""
        if v is None:
            return None

        # Handle the case where v might already be a datetime object
        if isinstance(v, datetime.datetime):
            dt = v
        else:
            # If it's not a datetime, let Pydantic handle the conversion
            # This will be handled by Pydantic's default datetime parsing
            return v

        # Check if the date is before 1990
        if dt.year < 1990:
            return None

        return dt

    @field_serializer('created', 'updated', 'added')
    def serialize_datetime(self, dt: Optional[datetime.datetime]) -> Optional[int]:
        """Serialize datetime fields to Unix timestamps"""
        return int(dt.timestamp()) if dt else None

    @field_validator('platform_summary', 'tagline', mode='before')
    @classmethod
    def parse_string(cls, v):
        if v is None:
            return ''
        return v  # [:1000]

    def get_text_for_embedding(self) -> str:
        """Override in subclasses"""
        raise NotImplementedError("Subclasses must implement get_text_for_embedding")


class SearchChar(SearchItemBase):
    """Character-specific search fields"""
    scenario: str = Field(..., description='The card scenario.')
    first_mes: str = Field(..., description='The card first message.')
    description: str = Field(..., description='The card description.')
    mes_example: str = Field(..., description='The card message example.')
    personality: str = Field(..., description='The card personality.')
    creator_notes: str = Field(..., description='The card creator notes.')
    system_prompt: str = Field(..., description='The card system prompt.')
    world_scenario: str = Field(..., description='The card world scenario.')
    example_dialogue: str = Field(..., description='The card example dialogue.')
    alternate_greetings: List[str] = Field(..., description='The card alternate greetings.')
    post_history_instructions: str = Field(..., description='The card post history instructions.')
    source_url: Optional[str] = Field(None, description='The original URL a card was sourced from. Only for generic cards.')

    # Override type with default value for character
    type: ItemTypes = Field(ItemTypes.character, description='The item type. "character" or "lorebook"')

    @field_validator(
        'scenario', 'first_mes', 'description', 'mes_example', 'personality',
        'creator_notes', 'system_prompt', 'world_scenario', 'example_dialogue',
        'post_history_instructions',
        mode='before')
    @classmethod
    def parse_character_strings(cls, v):
        if v is None:
            return ''
        return v  # [:1000]

    def get_text_for_embedding(self) -> str:
        text_fields = [
            self.name or '',
            self.scenario or '',
            self.first_mes or '',
            self.description or '',
            self.mes_example or '',
            self.personality or '',
            self.creator_notes or '',
            self.system_prompt or '',
            self.world_scenario or '',
            self.example_dialogue or '',
            self.post_history_instructions or '',
            self.platform_summary or '',
            self.tagline or ''
        ]
        return '\n\n'.join(text_fields)


class SearchLore(SearchItemBase):
    """Lorebook-specific search fields"""
    lore_content: List[str]

    # Override type with default value for lorebook
    type: ItemTypes = Field(ItemTypes.lorebook, description='The item type. "character" or "lorebook"')

    # Make created and updated required for lorebooks (they're optional in base)
    created: datetime.datetime = Field(..., description='The timestamp the lorebook was created.')
    updated: datetime.datetime = Field(..., description='The timestamp the lorebook was updated.')

    @field_validator('lore_content', mode='before')
    @classmethod
    def parse_list(cls, v: list):
        return v  # [x[:1000] for x in v]

    def get_text_for_embedding(self) -> str:
        text_fields = [
            self.name or '',
            self.tagline or '',
            self.platform_summary or '',
            ' '.join(self.lore_content) if self.lore_content else '',
        ]
        return ' '.join(text_fields)


def all_valid_search_keys():
    # Get all fields from base class
    base_fields = set(SearchItemBase.model_fields.keys())
    # Get character-specific fields (excluding those already in base)
    char_fields = set(k for k in SearchChar.model_fields.keys() if k not in base_fields or k == 'type')
    # Get lorebook-specific fields (excluding those already in base)
    lore_fields = set(k for k in SearchLore.model_fields.keys() if k not in base_fields or k == 'type')
    # Combine all unique fields, excluding 'chub'
    all_fields = (base_fields | char_fields | lore_fields) - {'chub'}
    return all_fields

from typing import Optional
from api.schemas.tags.base_schema import TagBaseSchema


class CreateTagRequest(TagBaseSchema):
    """Request schema for creating a tag"""
    tag_id: str


class CreateTagResponse(TagBaseSchema):
    """Response schema after creating a tag"""
    tag_id: str


from api.schemas.tags.base_schema import TagBaseSchema
from pydantic import BaseModel


class GetTagResponse(TagBaseSchema):
    """Response schema for getting a tag"""
    tag_id: str


class GetTagListResponse(BaseModel):
    """Schema for tag list response"""
    tags: list[GetTagResponse]
    total: int


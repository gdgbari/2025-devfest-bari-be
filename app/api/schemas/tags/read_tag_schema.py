from api.schemas.tags.base_schema import TagBaseSchemaWithSecret
from pydantic import BaseModel


class GetTagResponse(TagBaseSchemaWithSecret):
    """Response schema for getting a tag"""
    pass


class GetTagListResponse(BaseModel):
    """Schema for tag list response"""
    tags: list[GetTagResponse]
    total: int


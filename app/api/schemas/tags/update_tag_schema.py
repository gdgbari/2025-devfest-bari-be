from typing import Optional
from pydantic import BaseModel, Field

from api.schemas.tags.base_schema import TagBaseSchema


class UpdateTagRequest(BaseModel):
    """Schema for updating tag information"""
    points: Optional[int] = Field(None, description="Points value for the tag", ge=0)


class UpdateTagResponse(TagBaseSchema):
    """Response schema after updating a tag"""
    tag_id: str


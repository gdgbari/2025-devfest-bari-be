from typing import Optional
from pydantic import BaseModel, Field

from api.schemas.tags.base_schema import TagBaseSchemaWithSecret


class UpdateTagRequest(BaseModel):
    """Schema for updating tag information"""
    points: Optional[int] = Field(None, description="Points value for the tag", ge=0)


class UpdateTagResponse(TagBaseSchemaWithSecret):
    """Response schema after updating a tag"""
    pass


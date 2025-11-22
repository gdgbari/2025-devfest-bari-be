from pydantic import BaseModel, Field


class TagBaseSchema(BaseModel):
    """Base tag schema with common fields"""
    points: int = Field(..., description="Points value for the tag", ge=0)


from pydantic import BaseModel, Field


class TagBaseSchema(BaseModel):
    """Base tag schema with common fields"""
    points: int = Field(..., description="Points value for the tag", ge=0)
    tag_id: str = Field(..., description="Tag ID")

class TagBaseSchemaWithSecret(TagBaseSchema):
    """Tag schema with secret field"""
    secret: str = Field(..., description="Secret string for the tag")
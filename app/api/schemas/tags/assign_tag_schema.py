from pydantic import BaseModel, Field


class AssignTagRequest(BaseModel):
    """Request schema for assigning a tag to a user"""
    tag_id: str = Field(..., description="ID of the tag to assign")
    uid: str = Field(..., description="User ID to assign the tag to")


class AssignTagBySecretRequest(BaseModel):
    """Request schema for assigning a tag to a user by secret"""
    secret: str = Field(..., description="Secret string to redeem the tag")


class AssignTagResponse(BaseModel):
    """Response schema for assigning a tag to a user"""
    tag_id: str
    user_id: str
    points: int

class AssignTagBySecretResponse(BaseModel):
    """Response schema for assigning a tag to a user by secret"""
    secret: str
    user_id: str
    points: int

from base_schema import UserBaseSchema

from pydantic import BaseModel, Field

class GetUserResponse(UserBaseSchema):
    uid: str


class GetUserListResponse(BaseModel):
    """Schema for user list response"""

    users: list[GetUserResponse]
    total: int
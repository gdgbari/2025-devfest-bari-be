from typing import Optional
from api.schemas.users.base_schema import UserBaseSchema

from pydantic import BaseModel

class GetUserResponse(UserBaseSchema):
    uid: str
    group: Optional[str] = None


class GetUserListResponse(BaseModel):
    """Schema for user list response"""

    users: list[GetUserResponse]
    total: int

from typing import Optional, Dict, Any, List
from api.schemas.users.base_schema import UserBaseSchema
from api.schemas.tags.read_tag_schema import GetTagResponse

from pydantic import BaseModel

class GetUserResponse(UserBaseSchema):
    uid: str
    group: Optional[Dict[str, Any]] = None
    tags: Optional[List[GetTagResponse]] = None
    checked_in: bool = False
    role: Optional[str] = None


class GetUserListResponse(BaseModel):
    """Schema for user list response"""

    users: list[GetUserResponse]
    total: int

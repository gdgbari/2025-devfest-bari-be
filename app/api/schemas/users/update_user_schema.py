from typing import Optional

from api.schemas.users.base_schema import UserBaseSchema
from pydantic import BaseModel

class UpdateUserRequest(BaseModel):
    """Schema for updating user information"""

    email: Optional[str] = None
    name: Optional[str] = None
    surname: Optional[str] = None

class UpdateUserResponse(UserBaseSchema):
    uid: str
    group: Optional[str] = None

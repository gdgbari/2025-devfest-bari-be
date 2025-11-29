from typing import Optional
from pydantic import Field
from api.schemas.users.base_schema import UserBaseSchema

class CreateUserRequest(UserBaseSchema):
    password: str = Field(
        ..., min_length=8, description="Password must be at least 8 characters"
    )
    role: Optional[str] = "attendee"

class CreateUserResponse(UserBaseSchema):
    uid: str
    role: str

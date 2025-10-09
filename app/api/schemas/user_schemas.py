from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBaseSchema(BaseModel):
    """Base user schema with common fields"""

    email: EmailStr
    name: str
    surname: str
    nickname: str


class UserCreateSchema(UserBaseSchema):
    password: str = Field(
        ..., min_length=8, description="Password must be at least 8 characters"
    )


class UserResponseSchema(UserBaseSchema):
    uid: str


class UserUpdateSchema(BaseModel):
    """Schema for updating user information"""

    email: Optional[str] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    nickname: Optional[str] = None


class UserListResponseSchema(BaseModel):
    """Schema for user list response"""

    users: list[UserResponseSchema]
    total: int

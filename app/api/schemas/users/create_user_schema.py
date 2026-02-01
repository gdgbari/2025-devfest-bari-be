from typing import Optional
from pydantic import BaseModel, Field, EmailStr

class CreateUserRequest(BaseModel):
    email: EmailStr
    name: str
    surname: str
    nickname: str
    password: str = Field(
        ..., min_length=8, description="Password must be at least 8 characters"
    )
    role: Optional[str] = "attendee"

class CreateUserResponse(BaseModel):
    email: EmailStr
    name: str
    surname: str
    nickname: str
    uid: str
    role: str

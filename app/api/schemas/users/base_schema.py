from pydantic import BaseModel, EmailStr


class UserBaseSchema(BaseModel):
    """Base user schema with common fields"""

    email: EmailStr
    name: str
    surname: str
    nickname: str
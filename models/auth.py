from pydantic import BaseModel, EmailStr

class UserToken(BaseModel):
    user_id: str
    sub: str
    uid: str
    email: EmailStr
    email_verified: bool
    auth_time: int
    iat: int
    exp: int
    iss: str
    aud: str
    firebase: dict


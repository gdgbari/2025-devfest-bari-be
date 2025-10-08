from pydantic import BaseModel

class OkResponse(BaseModel):
    detail: str = "OK"

class RegistrationRequest(BaseModel):
    name:str
    surname: str
    nickname: str
    email: str
    password: str

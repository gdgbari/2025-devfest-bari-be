from pydantic import BaseModel

class RegistrationRequest(BaseModel):
    name:str
    surname: str
    nickname: str
    email: str
    password: str

from pydantic import BaseModel
from models.enums import UserRole

class User(BaseModel):
    uid: str
    email: str
    role: UserRole
    name:str
    surname: str
    nickname: str
    group: str | None = None
    
    def has_privileges(self, min_role: UserRole) -> bool:
        return self.role.is_authorized(min_role)
    
class RegistrationRequest(BaseModel):
    name:str
    surname: str
    nickname: str
    email: str
    password: str

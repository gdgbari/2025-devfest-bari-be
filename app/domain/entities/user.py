from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator

from domain.entities.role import Role

class User(BaseModel):
    """"
    Domain object representing the User
    """
    email: EmailStr
    name: str
    surname: str
    nickname: str
    uid: Optional[str] = None
    password: Optional[str] = None
    role: Optional[Role] = None
    group: Optional[str] = None

    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, v):
        if isinstance(v, str):
            return v.lower()
        return v

    @staticmethod
    def from_dict(data: dict) -> "User":
        return User(
            email=data["email"],
            name=data["name"],
            surname=data["surname"],
            nickname=data["nickname"],
            uid=data["uid"] if "uid" in data else None,
            role=data["role"] if "role" in data else None,
            group=data["group"] if "group" in data else None,
        )

    def to_firestore_data(self) -> dict:
        return {
            "email": self.email,
            "name": self.name,
            "surname": self.surname,
            "nickname": self.nickname,
            "role": self.role.value,
            "group": self.group
        }

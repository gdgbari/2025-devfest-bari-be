from typing import Optional

from pydantic import BaseModel, EmailStr

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

    @staticmethod
    def from_dict(data: dict) -> "User":
        return User(
            email=data["email"],
            name=data["name"],
            surname=data["surname"],
            nickname=data["nickname"],
            uid=data["uid"] if "uid" in data else None,
        )

    def to_firestore_data(self) -> dict:
        return {
            "email": self.email,
            "name": self.name,
            "surname": self.surname,
            "nickname": self.nickname,
        }

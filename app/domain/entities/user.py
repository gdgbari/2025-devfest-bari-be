from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel

from api.schemas.user_schemas import UserResponseSchema


@dataclass
class User:
    def __init__(
        self,
        email: str,
        name: str,
        surname: str,
        nickname: str,
        uid: Optional[str] = None,
        password: Optional[str] = None,
    ):
        self.email = email
        self.name = name
        self.surname = surname
        self.nickname = nickname
        self.uid = uid
        self.password = password

    def __repr__(self):
        return (
            f"User(\n"
            f"  uid={self.uid!r},\n"
            f"  email={self.email!r},\n"
            f"  name={self.name!r},\n"
            f"  surname={self.surname!r},\n"
            f"  nickname={self.nickname!r}\n"
            f")"
        )

    @staticmethod
    def from_dict(data: dict) -> "User":
        return User(
            email=data["email"],
            name=data["name"],
            surname=data["surname"],
            nickname=data["nickname"],
            uid=data["uid"] if "uid" in data else None,
        )

    @staticmethod
    def from_schema(schema: BaseModel) -> "User":
        data = schema.model_dump()
        return User.from_dict(data)

    def to_schema(self) -> UserResponseSchema:
        return UserResponseSchema(
            uid=self.uid,
            email=self.email,
            name=self.name,
            surname=self.surname,
            nickname=self.nickname,
        )

    def to_firestore_data(self) -> dict:
        return {
            "email": self.email,
            "name": self.name,
            "surname": self.surname,
            "nickname": self.nickname,
        }

    def to_update_data(self) -> dict:
        return {
            "name": self.name,
            "surname": self.surname,
            "nickname": self.nickname,
        }
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, EmailStr, field_validator

from domain.entities.role import Role
from domain.entities.tag import Tag

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
    group: Optional[Dict[str, Any]] = None
    tags: Optional[List[Tag]] = None  # List of Tag objects
    checked_in: bool = False

    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, v):
        if isinstance(v, str):
            return v.lower()
        return v

    @staticmethod
    def from_dict(data: dict, tags: Optional[List[Tag]] = None) -> "User":
        """
        Creates User from dict.
        Tags are passed separately as they need to be loaded from tags collection.
        """
        return User(
            email=data["email"],
            name=data["name"],
            surname=data["surname"],
            nickname=data["nickname"],
            uid=data["uid"] if "uid" in data else None,
            role=data["role"] if "role" in data else None,
            group=data["group"] if "group" in data else None,
            tags=tags,  # Tags loaded from tags collection
            checked_in=data.get("checked_in", False),
        )

    def to_firestore_data(self) -> dict:
        """
        Converts User to Firestore data.
        Tags are saved as list of tag_ids (documentIds).
        """
        result = {
            "email": self.email,
            "name": self.name,
            "surname": self.surname,
            "nickname": self.nickname,
            "role": self.role.value,
            "group": self.group,
            "checked_in": self.checked_in
        }
        if self.tags is not None:
            # Save tag_ids (documentIds) to Firestore
            tag_ids = [tag.tag_id for tag in self.tags if tag.tag_id]
            if tag_ids:
                result["tags"] = tag_ids
        return result

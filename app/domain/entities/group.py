from typing import Optional

from pydantic import BaseModel


class Group(BaseModel):
    """
    Domain object representing a Group
    """

    name: str
    color: str
    image_url: str
    user_count: Optional[int] = None
    gid: Optional[str] = None

    @staticmethod
    def from_dict(data: dict) -> "Group":
        return Group(
            name=data["name"],
            color=data["color"],
            image_url=data["imageUrl"],
            user_count=data["userCount"] if " userCount" in data else None,
            gid=data["gid"] if "gid" in data else None,
        )

    def to_firestore_data(self) -> dict:
        return {
            "name": self.name,
            "color": self.color,
            "imageUrl": self.image_url,
            "userCount": self.user_count,
        }


from typing import Optional
from pydantic import BaseModel


class Tag(BaseModel):
    """
    Domain object representing a Tag
    """
    tag_id: Optional[str] = None
    points: int
    secret: Optional[str] = None

    @staticmethod
    def from_dict(data: dict) -> "Tag":
        return Tag(
            tag_id=data.get("tag_id"),
            points=data.get("points", 0),
            secret=data.get("secret")
        )

    def to_firestore_data(self) -> dict:
        data = {
            "points": self.points
        }
        if self.secret is not None:
            data["secret"] = self.secret
        return data


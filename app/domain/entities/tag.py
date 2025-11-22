from typing import Optional
from pydantic import BaseModel


class Tag(BaseModel):
    """
    Domain object representing a Tag
    """
    tag_id: Optional[str] = None
    points: int

    @staticmethod
    def from_dict(data: dict) -> "Tag":
        return Tag(
            tag_id=data.get("tag_id"),
            points=data.get("points", 0)
        )

    def to_firestore_data(self) -> dict:
        return {
            "points": self.points
        }


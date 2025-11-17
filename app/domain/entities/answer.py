from pydantic import BaseModel


class Answer(BaseModel):
    """
    Domain object representing an Answer
    """

    id: str
    text: str

    @staticmethod
    def from_dict(data: dict) -> "Answer":
        return Answer(
            id=data["id"],
            text=data["text"]
        )

    def to_firestore_data(self) -> dict:
        return {
            "id": self.id,
            "text": self.text
        }


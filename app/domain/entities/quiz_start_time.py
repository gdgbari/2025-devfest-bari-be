from pydantic import BaseModel


class QuizStartTime(BaseModel):
    """
    Domain object representing when a user started a quiz
    """
    started_at: int  # milliseconds

    @staticmethod
    def from_dict(data: dict) -> "QuizStartTime":
        return QuizStartTime(
            started_at=data["started_at"]
        )

    def to_firestore_data(self) -> dict:
        return {
            "started_at": self.started_at
        }


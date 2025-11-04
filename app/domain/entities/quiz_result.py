from pydantic import BaseModel


class QuizResult(BaseModel):
    """
    Domain object representing a quiz result for a user
    """
    score: int
    max_score: int
    quiz_title: str
    submit_at: int  # milliseconds

    @staticmethod
    def from_dict(data: dict) -> "QuizResult":
        return QuizResult(
            score=data["score"],
            max_score=data["max_score"],
            quiz_title=data["quiz_title"],
            submit_at=data["submit_at"]
        )

    def to_firestore_data(self) -> dict:
        return {
            "score": self.score,
            "max_score": self.max_score,
            "quiz_title": self.quiz_title,
            "submit_at": self.submit_at
        }


from typing import List, Optional
from pydantic import BaseModel
from domain.entities.question import Question


class Quiz(BaseModel):
    """
    Domain object representing a Quiz
    """

    title: str
    question_list: List[Question]
    is_open: bool = False  # Default False
    timer_duration: int = 180000  # Default 3 minutes in milliseconds
    quiz_id: Optional[str] = None

    @staticmethod
    def from_dict(data: dict) -> "Quiz":
        return Quiz(
            title=data["title"],
            question_list=[Question.from_dict(q) for q in data["question_list"]],
            is_open=data.get("is_open", False),
            timer_duration=data.get("timer_duration", 180000),
            quiz_id=data.get("quiz_id") if "quiz_id" in data else None
        )

    def to_firestore_data(self) -> dict:
        return {
            "title": self.title,
            "question_list": [q.to_firestore_data() for q in self.question_list],
            "is_open": self.is_open,
            "timer_duration": self.timer_duration
        }


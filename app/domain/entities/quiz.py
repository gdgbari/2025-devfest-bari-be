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
            question_list=[Question.from_dict(q) for q in data["questionList"]],
            is_open=data.get("isOpen", False),
            timer_duration=data.get("timerDuration", 180000),
            quiz_id=data.get("quizId") if "quizId" in data else None
        )

    def to_firestore_data(self) -> dict:
        return {
            "title": self.title,
            "questionList": [q.to_firestore_data() for q in self.question_list],
            "isOpen": self.is_open,
            "timerDuration": self.timer_duration
        }


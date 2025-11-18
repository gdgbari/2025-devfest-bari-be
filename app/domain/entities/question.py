from typing import List, Optional
from pydantic import BaseModel
from domain.entities.answer import Answer


class Question(BaseModel):
    """
    Domain object representing a Question
    """

    text: str
    answer_list: List[Answer]
    correct_answer: str  # ID of the correct answer
    value: int = 10  # Default points
    question_id: Optional[str] = None  # Unique identifier for the question

    @staticmethod
    def from_dict(data: dict) -> "Question":
        return Question(
            text=data["text"],
            answer_list=[Answer.from_dict(ans) for ans in data["answer_list"]],
            correct_answer=data["correct_answer"],
            value=data.get("value", 10),
            question_id=data.get("question_id")
        )

    def to_firestore_data(self) -> dict:
        data = {
            "text": self.text,
            "answer_list": [ans.to_firestore_data() for ans in self.answer_list],
            "correct_answer": self.correct_answer,
            "value": self.value
        }
        if self.question_id is not None:
            data["question_id"] = self.question_id
        return data


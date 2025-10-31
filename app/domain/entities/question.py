from typing import List
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

    @staticmethod
    def from_dict(data: dict) -> "Question":
        return Question(
            text=data["text"],
            answer_list=[Answer.from_dict(ans) for ans in data["answerList"]],
            correct_answer=data["correctAnswer"],
            value=data.get("value", 10)
        )

    def to_firestore_data(self) -> dict:
        return {
            "text": self.text,
            "answerList": [ans.to_firestore_data() for ans in self.answer_list],
            "correctAnswer": self.correct_answer,
            "value": self.value
        }


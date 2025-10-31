from pydantic import BaseModel, Field
from typing import List


class AnswerSchema(BaseModel):
    """Answer schema"""
    id: str
    text: str


class QuestionSchema(BaseModel):
    """Question schema"""
    text: str
    answer_list: List[AnswerSchema]
    correct_answer: str = Field(..., description="ID of the correct answer")
    value: int = Field(default=10, description="Points for correct answer")


class QuizBaseSchema(BaseModel):
    """Base quiz schema with common fields"""
    title: str
    question_list: List[QuestionSchema]


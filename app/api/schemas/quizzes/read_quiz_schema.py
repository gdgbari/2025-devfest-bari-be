from pydantic import BaseModel, Field
from typing import List


class ReadAnswerSchema(BaseModel):
    """Answer schema for reading (no correct answer info)"""
    id: str
    text: str


class ReadQuestionSchema(BaseModel):
    """Question schema for reading (without correct answer)"""
    text: str
    answer_list: List[ReadAnswerSchema]
    value: int = Field(default=10, description="Points for correct answer")


class GetQuizResponse(BaseModel):
    """Response schema for getting a quiz"""
    quiz_id: str
    title: str
    question_list: List[ReadQuestionSchema]
    is_open: bool
    timer_duration: int = Field(..., description="Quiz duration in milliseconds")


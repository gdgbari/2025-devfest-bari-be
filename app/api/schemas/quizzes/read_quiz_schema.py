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


class ReadQuestionWithCorrectSchema(BaseModel):
    """Question schema for staff (includes correct answer)"""
    text: str
    answer_list: List[ReadAnswerSchema]
    correct_answer: str = Field(..., description="ID of the correct answer")
    value: int = Field(default=10, description="Points for correct answer")


class GetQuizResponse(BaseModel):
    """Response schema for getting a quiz"""
    quiz_id: str
    title: str
    question_list: List[ReadQuestionSchema]
    timer_duration: int = Field(..., description="Quiz duration in milliseconds")


class GetQuizWithCorrectResponse(BaseModel):
    """Response schema for getting a quiz with correct answers (staff only)"""
    quiz_id: str
    title: str
    question_list: List[ReadQuestionWithCorrectSchema]
    is_open: bool
    timer_duration: int = Field(..., description="Quiz duration in milliseconds")


class GetQuizListWithCorrectResponse(BaseModel):
    """Schema for quiz list response with correct answers (staff only)"""
    quizzes: List[GetQuizWithCorrectResponse]
    total: int


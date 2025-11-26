from typing import Optional, List
from pydantic import BaseModel, Field

from api.schemas.quizzes.base_schema import QuizBaseSchema, AnswerSchema


class UpdateQuestionSchema(BaseModel):
    """Question schema"""
    text: str
    answer_list: List[AnswerSchema]
    correct_answer: str = Field(..., description="ID of the correct answer")
    value: int = Field(..., description="Points for correct answer")
    question_id: Optional[str] = Field(None, description="Unique identifier for the question")


class UpdateQuizRequest(BaseModel):
    """Schema for updating quiz information"""

    title: Optional[str] = None
    question_list: Optional[List[UpdateQuestionSchema]] = None
    is_open: Optional[bool] = None
    session_id: Optional[str] = Field(None, description="Session ID associated with the quiz")


class UpdateQuizResponse(QuizBaseSchema):
    """Response schema after updating a quiz"""
    quiz_id: str
    is_open: bool
    timer_duration: int = Field(..., description="Quiz duration in milliseconds")


from typing import Optional, List
from pydantic import BaseModel, Field

from api.schemas.quizzes.base_schema import QuizBaseSchema, QuestionSchema


class UpdateQuizRequest(BaseModel):
    """Schema for updating quiz information"""

    title: Optional[str] = None
    question_list: Optional[List[QuestionSchema]] = None
    is_open: Optional[bool] = None


class UpdateQuizResponse(QuizBaseSchema):
    """Response schema after updating a quiz"""
    quiz_id: str
    is_open: bool
    timer_duration: int = Field(..., description="Quiz duration in milliseconds")


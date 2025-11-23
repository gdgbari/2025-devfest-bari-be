from pydantic import Field
from api.schemas.quizzes.base_schema import QuizBaseSchema
from typing import Optional


class CreateQuizRequest(QuizBaseSchema):
    """Request schema for creating a quiz"""
    # timer_duration is read from remote_config, not from request


class CreateQuizResponse(QuizBaseSchema):
    """Response schema after creating a quiz"""
    quiz_id: str
    is_open: bool
    timer_duration: int = Field(..., description="Quiz duration in milliseconds")


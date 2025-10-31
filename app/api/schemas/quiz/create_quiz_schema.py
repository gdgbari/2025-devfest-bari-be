from pydantic import Field
from api.schemas.quiz.base_schema import QuizBaseSchema


class CreateQuizRequest(QuizBaseSchema):
    """Request schema for creating a quiz"""
    # timer_duration is in MINUTES in the request body
    timer_duration: int = Field(default=3, description="Quiz duration in minutes")


class CreateQuizResponse(QuizBaseSchema):
    """Response schema after creating a quiz"""
    quiz_id: str
    is_open: bool
    timer_duration: int = Field(..., description="Quiz duration in milliseconds")


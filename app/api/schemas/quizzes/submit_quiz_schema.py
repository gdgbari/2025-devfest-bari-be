from pydantic import BaseModel, Field
from typing import List


class QuizAnswer(BaseModel):
    question_id: str = Field(..., description="The ID of the question")
    answer_id: str = Field(..., description="The ID of the selected answer")


class SubmitQuizRequest(BaseModel):
    """Request schema for submitting quiz answers"""
    answers: List[QuizAnswer] = Field(..., description="List of answers")


class SubmitQuizResponse(BaseModel):
    """Response schema for quiz submission"""
    score: int = Field(..., description="Points scored by the user")
    max_score: int = Field(..., description="Maximum points achievable for this quiz")


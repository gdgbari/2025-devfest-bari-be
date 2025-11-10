from pydantic import BaseModel, Field
from typing import List


class SubmitQuizRequest(BaseModel):
    """Request schema for submitting quiz answers"""
    answer_list: List[str] = Field(..., description="List of answer IDs selected by the user")


class SubmitQuizResponse(BaseModel):
    """Response schema for quiz submission"""
    score: int = Field(..., description="Points scored by the user")
    max_score: int = Field(..., description="Maximum points achievable for this quiz")


from typing import List
from pydantic import BaseModel

class UserQuizResultResponse(BaseModel):
    score: int
    max_score: int
    quiz_title: str
    submitted_at: int

class UserQuizResultListResponse(BaseModel):
    results: List[UserQuizResultResponse]

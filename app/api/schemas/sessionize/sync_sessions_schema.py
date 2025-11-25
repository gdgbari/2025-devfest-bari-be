from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


class SessionResponse(BaseModel):
    """Response schema for a single session"""
    id: str
    starts_at: datetime
    ends_at: datetime
    is_plenum_session: bool
    session_time_units: int = Field(..., description="Amount of hours")
    session_tags: List[str] = Field(..., description="List of tags associated with the session")


class SyncSessionsResponse(BaseModel):
    """Response schema for sync sessions endpoint"""
    sessions: List[SessionResponse] = Field(..., description="List of filtered sessions")
    session_count: int = Field(..., description="Total number of sessions")


from pydantic import BaseModel

class CheckInResponse(BaseModel):
    """Response schema for check-in operation"""
    uid: str
    group: dict

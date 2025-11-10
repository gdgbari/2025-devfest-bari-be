from pydantic import BaseModel

class CheckInResponse(BaseModel):
    """Response schema for check-in operation"""
    group: dict

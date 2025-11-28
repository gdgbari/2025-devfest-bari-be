from datetime import datetime
from typing import List
from pydantic import BaseModel


class Session(BaseModel):
    """
    Domain object representing a parsed session from Sessionize
    """
    id: str
    starts_at: datetime
    ends_at: datetime
    is_plenum_session: bool
    is_service_session: bool
    session_time_units: int  # Amount of hours
    session_tags: List[str]  # List of tags associated with the session

    @staticmethod
    def from_dict(data: dict) -> "Session":
        """
        Parses raw Sessionize API data (camelCase) into Session domain object.
        Sessionize format: {"id": "...", "startsAt": "...", "endsAt": "...", "isPlenumSession": bool}
        """
        starts_at_str = data["startsAt"]
        ends_at_str = data["endsAt"]

        starts_at = datetime.fromisoformat(starts_at_str.replace("Z", "+00:00"))
        ends_at = datetime.fromisoformat(ends_at_str.replace("Z", "+00:00"))

        return Session(
            id=str(data["id"]),
            starts_at=starts_at,
            ends_at=ends_at,
            is_plenum_session=data.get("isPlenumSession", False),
            is_service_session=data.get("isServiceSession", False),
            session_time_units=0,
            session_tags=[]
        )

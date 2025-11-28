from datetime import datetime
from pydantic import BaseModel, field_validator

class Slot(BaseModel):
    model_config = {'frozen': True}
    """
    Represents a time slot in the event schedule.
    """
    start: datetime
    end: datetime

    @field_validator("start", "end")
    @classmethod
    def strip_seconds(cls, v: datetime) -> datetime:
        return v.replace(second=0, microsecond=0)

    def __hash__(self):
        return hash((self.start, self.end))

from datetime import datetime
from pydantic import BaseModel

class Slot(BaseModel):
    model_config = {'frozen': True}
    """
    Represents a time slot in the event schedule.
    """
    start: datetime
    end: datetime

    def __hash__(self):
        return hash((self.start, self.end))

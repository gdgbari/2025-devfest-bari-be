from pydantic import BaseModel
from typing import Optional

class GroupBaseSchema(BaseModel):
    """Base group schema with common fields"""

    name: str
    color: str
    image_url: str
    user_count: Optional[int] = None


from pydantic import BaseModel


class GroupBaseSchema(BaseModel):
    """Base group schema with common fields"""

    name: str
    color: str
    image_url: str
    user_count: int


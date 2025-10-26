from typing import Optional

from pydantic import BaseModel

from api.schemas.groups.base_schema import GroupBaseSchema


class UpdateGroupRequest(BaseModel):
    """Schema for updating group information"""

    name: Optional[str] = None
    color: Optional[str] = None
    image_url: Optional[str] = None


class UpdateGroupResponse(GroupBaseSchema):
    gid: str


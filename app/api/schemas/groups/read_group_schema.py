from typing import Optional

from pydantic import BaseModel

from api.schemas.groups.base_schema import GroupBaseSchema


class GetGroupResponse(GroupBaseSchema):
    gid: str


class GetGroupListResponse(BaseModel):
    """Schema for group list response"""

    groups: list[GetGroupResponse]
    total: int


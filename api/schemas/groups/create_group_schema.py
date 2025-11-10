from api.schemas.groups.base_schema import GroupBaseSchema


class CreateGroupRequest(GroupBaseSchema):
    pass


class CreateGroupResponse(GroupBaseSchema):
    gid: str


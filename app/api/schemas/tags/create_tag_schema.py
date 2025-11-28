from api.schemas.tags.base_schema import TagBaseSchema, TagBaseSchemaWithSecret


class CreateTagRequest(TagBaseSchema):
    """Request schema for creating a tag"""
    pass


class CreateTagResponse(TagBaseSchemaWithSecret):
    """Response schema after creating a tag"""
    pass


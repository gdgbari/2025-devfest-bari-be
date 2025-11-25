from typing import Optional, List
from api.schemas.users.read_user_schema import *
from api.schemas.tags.read_tag_schema import GetTagResponse
from domain.entities.user import User
from domain.entities.tag import Tag

class ReadUserAdapters:
    """"
    Class with static methods used for converting request and response to domain objs
    for reading endpoints
    """

    @staticmethod
    def to_get_user_response(user: User) -> GetUserResponse:
        tags_response = None
        if user.tags:
            tags_response = [
                GetTagResponse(tag_id=tag.tag_id, points=tag.points)
                for tag in user.tags
                if tag.tag_id
            ]

        return GetUserResponse(
            uid=user.uid,
            email=user.email,
            name=user.name,
            surname=user.surname,
            nickname=user.nickname,
            group=user.group,
            tags=tags_response
        )

    @staticmethod
    def to_get_users_response(
        users: list[User],
    ) -> GetUserListResponse:
        return GetUserListResponse(
            users=[
                ReadUserAdapters.to_get_user_response(user)
                for user in users
            ],
            total=len(users),
        )

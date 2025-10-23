from api.schemas.users.read_user_schema import *
from domain.entities.user import User

class ReadUserAdapters:
    """"
    Class with static methods used for converting request and response to domain objs
    for reading endpoints
    """
    
    @staticmethod
    def to_get_user_response(user: User) -> GetUserResponse:
        return GetUserResponse(
            uid=user.uid,
            email=user.email,
            name=user.name,
            surname=user.surname,
            nickname=user.nickname,
            role=user.role,
            group=user.group
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
from api.schemas.users.read_user_schema import *
from domain.entities.user import User

class ReadUserAdapters:
    
    @staticmethod
    def to_get_user_response(user: User) -> GetUserResponse:
        return GetUserResponse(
            uid=user.uid,
            email=user.email,
            name=user.name,
            surname=user.surname,
            nickname=user.nickname,
        )
    
    @staticmethod
    def to_get_users_response(
        users: list[User],
    ) -> GetUserListResponse:
        return GetUserListResponse(
            users=[
                GetUserResponse(
                    uid=user.uid,
                    email=user.email,
                    name=user.name,
                    surname=user.surname,
                    nickname=user.nickname,
                )
                for user in users
            ],
            total=len(users),
        )
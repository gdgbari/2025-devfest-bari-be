from api.schemas.users.update_user_schema import *
from domain.entities.user import User

class UpdateUserAdapters:
    """"
    Class with static methods used for converting request and response to domain objs
    for updating endpoints
    """

    @staticmethod
    def to_update_response(user: User) -> UpdateUserResponse:
        return UpdateUserResponse(
            uid=user.uid,
            email=user.email,
            name=user.name,
            surname=user.surname,
            nickname=user.nickname,
            role=user.role,
            group=user.group
        )

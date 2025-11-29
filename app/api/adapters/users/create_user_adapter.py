from api.schemas.users.create_user_schema import *
from domain.entities.user import User
from domain.entities.role import Role

class CreateUserAdapter:
    """"
    Class with static methods used for converting request and response to domain objs
    for creation endpoints
    """
    
    @staticmethod
    def to_create_user_domain(user: CreateUserRequest) -> User:
        return User(
            email=user.email,
            name=user.name,
            surname=user.surname,
            nickname=user.nickname,
            password=user.password,
            role=user.role,
            group=None
        )

    @staticmethod
    def to_create_user_response(user: User) -> CreateUserResponse:
        return CreateUserResponse(
            uid=user.uid,
            email=user.email,
            name=user.name,
            surname=user.surname,
            nickname=user.nickname,
            role=user.role.value if user.role else "attendee"
        )
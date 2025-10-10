from api.schemas.users.create_user_schema import *
from domain.entities.user import User

class CreateUserAdapter:
    @staticmethod
    def to_create_user_domain(user: CreateUserRequest) -> User:
        return User(
            email=user.email,
            name=user.name,
            surname=user.surname,
            nickname=user.nickname,
            password=user.password,
        )

    @staticmethod
    def to_create_user_response(user: User) -> CreateUserResponse:
        return CreateUserResponse(
            uid=user.uid,
            email=user.email,
            name=user.name,
            surname=user.surname,
            nickname=user.nickname,
        )
from api.schemas.user_schemas import *
from domain.entities.user import User


class UserAdapters:
    @staticmethod
    def create_schema_to_domain(user: UserCreateSchema) -> User:
        return User(
            email=user.email,
            name=user.name,
            surname=user.surname,
            nickname=user.nickname,
            password=user.password,
        )

    @staticmethod
    def domain_to_response_schema(user: User) -> UserResponseSchema:
        return UserResponseSchema(
            uid=user.uid,
            email=user.email,
            name=user.name,
            surname=user.surname,
            nickname=user.nickname,
        )

    @staticmethod
    def domain_list_to_list_response_schema(
        users: list[User],
    ) -> UserListResponseSchema:
        return UserListResponseSchema(
            users=[
                UserResponseSchema(
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

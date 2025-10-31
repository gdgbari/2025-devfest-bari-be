from fastapi import FastAPI, HTTPException, Request, status

from infrastructure.errors.user_errors import *
from infrastructure.errors.auth_errors import *
from infrastructure.errors.group_errors import *
from infrastructure.errors.config_errors import *
from infrastructure.errors.quiz_errors import *

def register_exception_handlers(app: FastAPI):
    """Register all global exception handlers"""

    @app.exception_handler(ReserveNicknameError)
    async def reserve_nickname_error_handler(request: Request, exc: ReserveNicknameError):
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    @app.exception_handler(CreateUserError)
    async def create_user_error_handler(request: Request, exc: CreateUserError):
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    @app.exception_handler(AuthenticateUserError)
    async def authenticate_user_error_handler(request: Request, exc: AuthenticateUserError):
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    @app.exception_handler(DeleteUserError)
    async def delete_user_error_handler(request: Request, exc: DeleteUserError):
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    @app.exception_handler(DeleteUserAuthError)
    async def delete_user_auth_error_handler(request: Request, exc: DeleteUserAuthError):
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    @app.exception_handler(ReadUserError)
    async def read_user_error_handler(request: Request, exc: ReadUserError):
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    @app.exception_handler(UpdateUserAuthError)
    async def update_user_auth_error_handler(request: Request, exc: UpdateUserAuthError):
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    @app.exception_handler(UpdateUserError)
    async def update_user_auth_error_handler(request: Request, exc: UpdateUserError):
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    @app.exception_handler(UnauthorizedError)
    async def unauthorized_error_handler(request: Request, exc: UnauthorizedError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not Authorized",
        )

    @app.exception_handler(ForbiddenError)
    async def forbidden_error_handler(request: Request, exc: ForbiddenError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient Permissions",
        )

    @app.exception_handler(CreateGroupError)
    async def create_group_error_handler(request: Request, exc: CreateGroupError):
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    @app.exception_handler(ReadGroupError)
    async def read_group_error_handler(request: Request, exc: ReadGroupError):
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    @app.exception_handler(UpdateGroupError)
    async def update_group_error_handler(request: Request, exc: UpdateGroupError):
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    @app.exception_handler(DeleteGroupError)
    async def delete_group_error_handler(request: Request, exc: DeleteGroupError):
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    @app.exception_handler(ReadConfigError)
    async def read_config_error_handler(request: Request, exc: ReadConfigError):
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    @app.exception_handler(CheckInNotOpenError)
    async def check_in_not_open_error_handler(request: Request, exc: CheckInNotOpenError):
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    @app.exception_handler(CreateQuizError)
    async def create_quiz_error_handler(request: Request, exc: CreateQuizError):
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    @app.exception_handler(ReadQuizError)
    async def read_quiz_error_handler(request: Request, exc: ReadQuizError):
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    @app.exception_handler(UpdateQuizError)
    async def update_quiz_error_handler(request: Request, exc: UpdateQuizError):
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    @app.exception_handler(DeleteQuizError)
    async def delete_quiz_error_handler(request: Request, exc: DeleteQuizError):
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        raise HTTPException(status_code=500, detail="Internal server error")

from fastapi import FastAPI, HTTPException, Request

from infrastructure.errors.user_errors import *
from infrastructure.errors.auth_errors import *

def register_exception_handlers(app: FastAPI):
    """Register all global exception handlers"""

    @app.exception_handler(ReserveNicknameError)
    async def reserve_nickname_error_handler(request: Request, exc: ReserveNicknameError):
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    @app.exception_handler(CreateUserError)
    async def create_user_error_handler(request: Request, exc: ReserveNicknameError):
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

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        raise HTTPException(status_code=500, detail=str(exc))

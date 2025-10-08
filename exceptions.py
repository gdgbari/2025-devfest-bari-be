from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

class AppException(Exception):
    """Base exception for application errors"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class FeatureNotImplementedError(AppException):
    """Raised when a feature is not yet implemented"""
    def __init__(self, message: str = "Feature not implemented"):
        super().__init__(message, status_code=501)

class EmailAlreadyExistsError(AppException):
    """Raised when the email is already existing during the registration"""
    def __init__(self, message: str = "Email already existing"):
        super().__init__(message, status_code=400)

class RegistrationError(AppException):
    """Raised when there's a generic error during the registration"""
    def __init__(self, message: str = "Registration error"):
        super().__init__(message, status_code=400)

class NicknameAlreadyExistsError(AppException):
    """Raised when the nickname is already existing during the registration"""
    def __init__(self, message: str = "Nickname already existing"):
        super().__init__(message, status_code=400)


def register_exception_handlers(app: FastAPI):
    """Register all global exception handlers"""

    @app.exception_handler(FeatureNotImplementedError)
    async def feature_not_implemented_handler(request: Request, exc: FeatureNotImplementedError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message}
        )

    @app.exception_handler(EmailAlreadyExistsError)
    async def email_already_exiting_handler(request: Request, exc: EmailAlreadyExistsError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message}
        )

    @app.exception_handler(RegistrationError)
    async def registration_error_handler(request: Request, exc: RegistrationError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message}
        )

    @app.exception_handler(NicknameAlreadyExistsError)
    async def nickname_already_exists_handler(request: Request, exc: NicknameAlreadyExistsError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message}
        )


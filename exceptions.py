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


def register_exception_handlers(app: FastAPI):
    """Register all global exception handlers"""

    @app.exception_handler(FeatureNotImplementedError)
    async def feature_not_implemented_handler(request: Request, exc: FeatureNotImplementedError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message}
        )

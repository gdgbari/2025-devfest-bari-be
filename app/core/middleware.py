from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.settings import settings


async def enforce_prefix(request: Request, call_next):
    """
    Middleware to enforce that all incoming requests start with the API root path.

    If the request path does not start with the configured API root path,
    a 404 Not Found response is returned.

    Args:
        request (Request): The incoming HTTP request.
        call_next (Callable): The next middleware or route handler.

    Returns:
        Response: The response from the next middleware or a 404 JSON response.
    """
    if not request.url.path.startswith(settings.api_root_path):
        return JSONResponse(status_code=404, content={"detail": "Not Found"})
    return await call_next(request)


async def remove_trailing_slash(request: Request, call_next):
    """
    Middleware to remove a trailing slash from the request path.

    If the request path ends with a slash, it is removed before passing
    the request to the next middleware or route handler.

    Args:
        request (Request): The incoming HTTP request.
        call_next (Callable): The next middleware or route handler.

    Returns:
        Response: The response from the next middleware or route handler.
    """
    if request.url.path.endswith("/"):
        request.scope["path"] = request.url.path[:-1]
    return await call_next(request)


def add_middlewares(app: FastAPI) -> None:
    """
    Register all HTTP middlewares with the FastAPI application.

    This function adds CORS middleware if debug mode is enabled and
    registers custom HTTP middlewares for prefix enforcement and
    trailing slash removal.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    if settings.debug:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    middlewares = [
        enforce_prefix,
        remove_trailing_slash,
    ]

    for middleware in middlewares:
        app.middleware("http")(middleware)

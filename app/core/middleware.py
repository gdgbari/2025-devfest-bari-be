from core.settings import settings
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


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
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.debug else ["https://bari.devfest.it"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    middlewares = [
        remove_trailing_slash,
    ]

    for middleware in middlewares:
        app.middleware("http")(middleware)

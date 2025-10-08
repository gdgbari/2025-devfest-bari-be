import uvicorn
import os
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings
from utils import load_routers, TrailingSlashMiddleware
from exceptions import register_exception_handlers

# Load application settings
settings = get_settings()

os.chdir(os.path.dirname(os.path.realpath(__file__)))

app = FastAPI(
    debug=settings.debug,
    redoc_url=None,
    docs_url="/api/docs",
    version=settings.version,
    title=settings.title,
    responses={
        403: {
            "description": "Authentication Error",
            "content": {
                "application/json": {
                    "example": [
                        {"detail": "Not authenticated"},
                        {"detail": "User not correctly registered"}
                    ],
                    "schema": {"type": "object", "properties": {"detail": {"type": "string"}}}
                }
            }
        },
        401: {
            "description": "You don't have the required privileges to access this resource",
            "content": {
                "application/json": {
                    "example": {"detail": "You don't have the required privileges to access this resource"},
                    "schema": {"type": "object", "properties": {"detail": {"type": "string"}}}
                }
            }
        }
    }

)

# This middleware allows requests like /path/ to be redirected to /path
# This will require to NEVER define routes with trailing slash (i.e. @app.get("/path/") is not allowed, use @app.get("/path") instead)
app.add_middleware(TrailingSlashMiddleware)
register_exception_handlers(app)

api = APIRouter(prefix="/api")
load_routers(api)
app.include_router(api)

if settings.debug:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

if __name__ == '__main__':
    uvicorn.run(
        "app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        access_log=True,
        workers=settings.nthreads
    )

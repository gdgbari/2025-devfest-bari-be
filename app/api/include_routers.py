from fastapi import APIRouter, FastAPI

from api.routers.health.health import router as health_router
from api.routers.users import router as users_router

api_router = APIRouter(prefix="/api")


def include_routers(app: FastAPI) -> None:
    api_router.include_router(health_router)
    api_router.include_router(users_router)

    app.include_router(api_router)

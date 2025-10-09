from fastapi import FastAPI

from api.routers.users.create_user import router as create_users_router
from api.routers.users.update_user import router as update_users_router
from api.routers.users.read_user import router as read_users_router
from api.routers.users.delete_user import router as delete_users_router
from api.routers.health.health import router as health_router


def include_routers(app: FastAPI) -> None:
    app.include_router(health_router)
    app.include_router(create_users_router)
    app.include_router(update_users_router)
    app.include_router(read_users_router)
    app.include_router(delete_users_router)

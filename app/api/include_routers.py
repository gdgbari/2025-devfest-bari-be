from fastapi import FastAPI

from api.routers.users import router as users_router
from api.routers.root import router as root_router


def include_routers(app: FastAPI) -> None:
    app.include_router(root_router)
    app.include_router(users_router)

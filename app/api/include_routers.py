from api.routers.groups import router as groups_router
from api.routers.health.health import router as health_router
from api.routers.quizzes import router as quiz_router
from api.routers.sessionize import router as sessionize_router
from api.routers.tags import router as tags_router
from api.routers.users import router as users_router
from fastapi import APIRouter, FastAPI

api_router = APIRouter(prefix="/api")


def include_routers(app: FastAPI) -> None:
    api_router.include_router(health_router)
    api_router.include_router(users_router)
    api_router.include_router(groups_router)
    api_router.include_router(quiz_router)
    api_router.include_router(sessionize_router)
    api_router.include_router(tags_router)
    
    from api.routers.admin.reset_data import router as admin_router
    api_router.include_router(admin_router)

    app.include_router(api_router)

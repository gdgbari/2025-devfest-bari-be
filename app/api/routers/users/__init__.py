from fastapi import APIRouter

from .create_user import router as create_user_router
from .delete_user import router as delete_user_router
from .read_user import router as read_user_router
from .update_user import router as update_user_router

router = APIRouter()

router.include_router(create_user_router)
router.include_router(read_user_router)
router.include_router(update_user_router)
router.include_router(delete_user_router)

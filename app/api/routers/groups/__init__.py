from fastapi import APIRouter

from .create_group import router as create_group_router
from .delete_group import router as delete_group_router
from .read_group import router as read_group_router
from .update_group import router as update_group_router

router = APIRouter()

router.include_router(create_group_router)
router.include_router(read_group_router)
router.include_router(update_group_router)
router.include_router(delete_group_router)


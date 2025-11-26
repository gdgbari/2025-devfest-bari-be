from fastapi import APIRouter

from .create_tag import router as create_tag_router
from .delete_tag import router as delete_tag_router
from .read_tag import router as read_tag_router
from .update_tag import router as update_tag_router
from .assign_tag import router as assign_tag_router

router = APIRouter()

router.include_router(create_tag_router)
router.include_router(read_tag_router)
router.include_router(update_tag_router)
router.include_router(delete_tag_router)
router.include_router(assign_tag_router)


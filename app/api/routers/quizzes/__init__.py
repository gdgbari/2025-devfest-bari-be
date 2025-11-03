from fastapi import APIRouter

from .create_quiz import router as create_quiz_router
from .delete_quiz import router as delete_quiz_router
from .read_quiz import router as read_quiz_router

router = APIRouter()

router.include_router(create_quiz_router)
router.include_router(delete_quiz_router)
router.include_router(read_quiz_router)


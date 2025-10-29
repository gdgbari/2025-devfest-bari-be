from fastapi import APIRouter

from .check_in import router as check_in_router
router = APIRouter()

router.include_router(check_in_router)
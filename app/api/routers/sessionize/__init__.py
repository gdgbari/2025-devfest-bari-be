from fastapi import APIRouter
from .get_all import router as get_all_router
from .get_grid_smart import router as get_grid_smart_router
from .get_sessions import router as get_sessions_router
from .get_speakers import router as get_speakers_router
from .get_speaker_wall import router as get_speaker_wall_router

router = APIRouter(prefix="/sessionize", tags=["Sessionize"])

router.include_router(get_all_router)
router.include_router(get_grid_smart_router)
router.include_router(get_sessions_router)
router.include_router(get_speakers_router)
router.include_router(get_speaker_wall_router)

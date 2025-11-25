from fastapi import APIRouter, Depends, status

from core.dependencies import SessionServiceDep
from core.authorization import check_user_role, verify_id_token
from api.adapters.sessionize.sync_sessions_adapter import SyncSessionsAdapter
from api.schemas.sessionize.sync_sessions_schema import SyncSessionsResponse

router = APIRouter()

@router.post(
    "/sync-sessions",
    description="Sync Sessionize sessions with quizzes and update quiz sessions field",
    status_code=status.HTTP_200_OK,
    response_model=SyncSessionsResponse,
)
async def sync_sessions(
    session_service: SessionServiceDep,
    user_token=Depends(verify_id_token),
) -> SyncSessionsResponse:
    """
    Syncs Sessionize sessions with quizzes.
    Updates each quiz's sessions field based on session_id.
    Requires staff role.
    """
    check_user_role(user_token)

    sessions = await session_service.map_sessions_to_quizzes()

    return SyncSessionsAdapter.to_sync_sessions_response(sessions)

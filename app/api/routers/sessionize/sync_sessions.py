from fastapi import APIRouter, Depends, status

from core.dependencies import SessionServiceDep
from core.authorization import check_user_role, verify_id_token
from domain.entities.user import User
from domain.entities.role import Role
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
    user_token: User = Depends(verify_id_token),
) -> None:
    """
    Manually trigger session sync from Sessionize.
    """
    check_user_role(user_token, min_role=Role.STAFF)
    
    await session_service.sync_sessions()
    return None

from api.schemas.sessionize.sync_sessions_schema import SessionResponse, SyncSessionsResponse
from domain.entities.session import Session


class SyncSessionsAdapter:
    """
    Class with static methods used for converting domain objects to response
    for sync sessions endpoint
    """

    @staticmethod
    def to_session_response(session: Session) -> SessionResponse:
        """Convert Session domain object to SessionResponse"""
        return SessionResponse(
            id=session.id,
            starts_at=session.starts_at,
            ends_at=session.ends_at,
            is_plenum_session=session.is_plenum_session,
            session_time_units=session.session_time_units,
            session_tags=session.session_tags
        )

    @staticmethod
    def to_sync_sessions_response(sessions: list[Session]) -> SyncSessionsResponse:
        """Convert list of Session domain objects to SyncSessionsResponse"""
        return SyncSessionsResponse(
            sessions=[
                SyncSessionsAdapter.to_session_response(session)
                for session in sessions
            ],
            session_count=len(sessions)
        )


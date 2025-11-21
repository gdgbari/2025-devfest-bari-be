from fastapi import APIRouter, status
from infrastructure.clients.sessionize_client import SessionizeClient

router = APIRouter()


@router.get(
    "/sessions",
    description="Get sessions from Sessionize",
    status_code=status.HTTP_200_OK,
)
async def get_sessions():
    client = SessionizeClient()
    return await client.get_sessions()

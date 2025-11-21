from fastapi import APIRouter, status
from infrastructure.clients.sessionize_client import SessionizeClient

router = APIRouter()


@router.get(
    "/speaker-wall",
    description="Get speaker wall from Sessionize",
    status_code=status.HTTP_200_OK,
)
async def get_speaker_wall():
    client = SessionizeClient()
    return await client.get_speaker_wall()

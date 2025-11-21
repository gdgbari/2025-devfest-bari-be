from fastapi import APIRouter, status
from infrastructure.clients.sessionize_client import SessionizeClient

router = APIRouter()


@router.get(
    "/speakers",
    description="Get speakers from Sessionize",
    status_code=status.HTTP_200_OK,
)
async def get_speakers():
    client = SessionizeClient()
    return await client.get_speakers()

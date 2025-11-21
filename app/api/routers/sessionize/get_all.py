from fastapi import APIRouter, status
from infrastructure.clients.sessionize_client import SessionizeClient

router = APIRouter()


@router.get(
    "/all",
    description="Get all data from Sessionize",
    status_code=status.HTTP_200_OK,
)
async def get_all():
    client = SessionizeClient()
    return await client.get_all()

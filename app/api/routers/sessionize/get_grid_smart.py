from fastapi import APIRouter, status
from infrastructure.clients.sessionize_client import SessionizeClient

router = APIRouter()


@router.get(
    "/grid-smart",
    description="Get GridSmart view from Sessionize",
    status_code=status.HTTP_200_OK,
)
async def get_grid_smart():
    client = SessionizeClient()
    return await client.get_grid_smart()

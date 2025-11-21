import httpx
from typing import Any, Dict, List, Optional
from core.settings import settings


class SessionizeClient:
    """
    Client for interacting with the Sessionize API.
    """

    BASE_URL = "https://sessionize.com/api/v2"

    def __init__(self):
        self.sessionize_id = settings.sessionize_id
        self.base_url = f"{self.BASE_URL}/{self.sessionize_id}"

    async def get_all(self) -> Dict[str, Any]:
        """
        Fetches all data from Sessionize.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/view/All")
            response.raise_for_status()
            return response.json()

    async def get_grid_smart(self) -> List[Dict[str, Any]]:
        """
        Fetches the GridSmart view from Sessionize.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/view/GridSmart")
            response.raise_for_status()
            return response.json()

    async def get_sessions(self) -> List[Dict[str, Any]]:
        """
        Fetches the sessions from Sessionize.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/view/Sessions")
            response.raise_for_status()
            return response.json()

    async def get_speakers(self) -> List[Dict[str, Any]]:
        """
        Fetches the speakers from Sessionize.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/view/Speakers")
            response.raise_for_status()
            return response.json()

    async def get_speaker_wall(self) -> List[Dict[str, Any]]:
        """
        Fetches the speaker wall from Sessionize.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/view/SpeakerWall")
            response.raise_for_status()
            return response.json()

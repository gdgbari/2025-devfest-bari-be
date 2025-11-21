from typing import Any, Dict, List, Optional

import httpx
from cachetools import TTLCache
from core.settings import settings


class SessionizeClient:
    """
    Client for interacting with the Sessionize API.
    """

    BASE_URL = "https://sessionize.com/api/v2"
    cache = TTLCache(maxsize=5, ttl=600)

    def __init__(self):
        self.sessionize_id = settings.sessionize_id
        self.base_url = f"{self.BASE_URL}/{self.sessionize_id}"

    async def _get_cached_or_fetch(self, view_name: str) -> Any:
        if view_name in self.cache:
            return self.cache[view_name]

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/view/{view_name}")
            response.raise_for_status()
            data = response.json()
            self.cache[view_name] = data
            return data

    async def get_all(self) -> Dict[str, Any]:
        """
        Fetches all data from Sessionize.
        """
        return await self._get_cached_or_fetch("All")

    async def get_grid_smart(self) -> List[Dict[str, Any]]:
        """
        Fetches the GridSmart view from Sessionize.
        """
        return await self._get_cached_or_fetch("GridSmart")

    async def get_sessions(self) -> List[Dict[str, Any]]:
        """
        Fetches the sessions from Sessionize.
        """
        return await self._get_cached_or_fetch("Sessions")

    async def get_speakers(self) -> List[Dict[str, Any]]:
        """
        Fetches the speakers from Sessionize.
        """
        return await self._get_cached_or_fetch("Speakers")

    async def get_speaker_wall(self) -> List[Dict[str, Any]]:
        """
        Fetches the speaker wall from Sessionize.
        """
        return await self._get_cached_or_fetch("SpeakerWall")

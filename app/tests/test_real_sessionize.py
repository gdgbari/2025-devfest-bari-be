import asyncio
from unittest.mock import MagicMock
from domain.services.session_service import SessionService
from infrastructure.clients.sessionize_client import SessionizeClient
from core.settings import settings
import httpx

async def test_real_sessionize():
    # Override settings with the provided ID
    settings.sessionize_id = "i9otum6s"
    
    # Instantiate real client
    client = SessionizeClient()
    
    # Patch _get_cached_or_fetch to use a longer timeout if needed, or just rely on default
    # But since we got a timeout, let's try to patch the client usage inside SessionizeClient
    # Actually, SessionizeClient creates a new AsyncClient every time.
    # Let's monkeypatch httpx.AsyncClient to have a longer default timeout
    
    original_init = httpx.AsyncClient.__init__
    
    def new_init(self, *args, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = 30.0
        original_init(self, *args, **kwargs)
        
    httpx.AsyncClient.__init__ = new_init
    
    # Mock quiz repo (we don't want to write to DB)
    quiz_repo = MagicMock()
    quiz_repo.read_all.return_value = []
    
    service = SessionService(client, quiz_repo)
    
    print(f"Fetching sessions from Sessionize (ID: {settings.sessionize_id})...")
    await service.map_sessions_to_quizzes()
    
    # We can't assert specific slots without knowing the data, but we can print them
    # The debug prints in SessionService will show the slots
    print("\nTest completed. Check debug output above for generated slots.")

if __name__ == "__main__":
    asyncio.run(test_real_sessionize())

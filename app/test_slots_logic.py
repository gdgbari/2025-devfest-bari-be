import asyncio
from unittest.mock import MagicMock
from datetime import datetime, timedelta
from domain.services.session_service import SessionService
from domain.entities.session import Session
from domain.entities.slot import Slot

async def test_slots_logic():
    # Mock dependencies
    sessionize_client = MagicMock()
    quiz_repo = MagicMock()
    
    service = SessionService(sessionize_client, quiz_repo)
    
    # Setup sessions based on user example
    # S1: 10:00 - 10:50
    # S2: 10:50 - 11:40
    # Service: 11:40 - 12:00 (20m)
    # S3: 12:00 - 12:50
    # Lunch: 12:50 - 14:00 (Service)
    # S4: 14:00 - 14:50
    
    sessions = [
        Session(id="s1", starts_at=datetime(2025, 11, 29, 10, 0), ends_at=datetime(2025, 11, 29, 10, 50), is_plenum_session=False, is_service_session=False, session_time_units=1, session_tags=[]),
        Session(id="s2", starts_at=datetime(2025, 11, 29, 10, 50), ends_at=datetime(2025, 11, 29, 11, 40), is_plenum_session=False, is_service_session=False, session_time_units=1, session_tags=[]),
        Session(id="serv1", starts_at=datetime(2025, 11, 29, 11, 40), ends_at=datetime(2025, 11, 29, 12, 0), is_plenum_session=False, is_service_session=True, session_time_units=0, session_tags=[]),
        Session(id="s3", starts_at=datetime(2025, 11, 29, 12, 0), ends_at=datetime(2025, 11, 29, 12, 50), is_plenum_session=False, is_service_session=False, session_time_units=1, session_tags=[]),
        Session(id="lunch", starts_at=datetime(2025, 11, 29, 12, 50), ends_at=datetime(2025, 11, 29, 14, 0), is_plenum_session=False, is_service_session=True, session_time_units=0, session_tags=[]),
        Session(id="s4", starts_at=datetime(2025, 11, 29, 14, 0), ends_at=datetime(2025, 11, 29, 14, 50), is_plenum_session=False, is_service_session=False, session_time_units=1, session_tags=[]),
    ]
    
    print("Running _calculate_and_map_slots...")
    service._calculate_and_map_slots(sessions)
    
    # Verify slots
    slots_s1 = service.get_slots_for_session("s1")
    slots_s2 = service.get_slots_for_session("s2")
    slots_s3 = service.get_slots_for_session("s3")
    slots_s4 = service.get_slots_for_session("s4")
    
    print(f"S1 slots: {slots_s1}")
    print(f"S2 slots: {slots_s2}")
    print(f"S3 slots: {slots_s3}")
    print(f"S4 slots: {slots_s4}")
    
    # Expected behavior:
    # S1: 10:00-10:50
    # S2: 10:50-11:40
    # S3: 12:00-12:50 (Skipping 11:40-12:00 service)
    # S4: 14:00-14:50 (Skipping 12:50-14:00 lunch)
    
    assert len(slots_s1) == 1
    assert slots_s1[0].start == datetime(2025, 11, 29, 10, 0)
    
    assert len(slots_s2) == 1
    assert slots_s2[0].start == datetime(2025, 11, 29, 10, 50)
    
    assert len(slots_s3) == 1
    assert slots_s3[0].start == datetime(2025, 11, 29, 12, 0)
    
    assert len(slots_s4) == 1
    assert slots_s4[0].start == datetime(2025, 11, 29, 14, 0)
    
    print("SUCCESS: Slots generated correctly with service skipping.")

if __name__ == "__main__":
    asyncio.run(test_slots_logic())

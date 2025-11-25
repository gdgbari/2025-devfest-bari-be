from datetime import datetime
from typing import Dict, List
from math import ceil
from collections import defaultdict

from infrastructure.clients.sessionize_client import SessionizeClient
from domain.entities.session import Session
from infrastructure.repositories.quiz_repository import QuizRepository
from infrastructure.errors.quiz_errors import UpdateQuizError

class SessionService:
    """
    Service that syncs Sessionize sessions with quizzes
    """

    def __init__(
        self,
        sessionize_client: SessionizeClient,
        quiz_repository: QuizRepository
    ):
        self.sessionize_client = sessionize_client
        self.quiz_repository = quiz_repository


    async def map_sessions_to_quizzes(self) -> List[Session]:
        """
        Maps Sessionize sessions to quizzes by updating quiz sessions field.

        Returns:
            List of sessions
        """
        # Get all sessions from all groups
        groups_data = await self.sessionize_client.get_sessions()

        # Extract all sessions from all groups
        all_raw_sessions = []
        for group in groups_data:
            all_raw_sessions.extend(group["sessions"])

        # Parse sessions
        sessions = [Session.from_dict(session) for session in all_raw_sessions]

        # Filter and calculate time units
        filtered_sessions = self._filter_sessions(sessions)

        # Assign session tags based on start time
        sessions_with_tags = self._assign_session_tags(filtered_sessions)

        # Update quizzes with sessions
        self._update_quizzes_with_sessions(sessions_with_tags)

        return sessions_with_tags


    def _filter_sessions(self, sessions: List[Session]) -> List[Session]:
        """
        Filters sessions to only include non-plenum sessions,
        and calculate the amount of hours each session takes, ceil rounded up.
        """
        parsed = []

        for session in sessions:
            if session.is_plenum_session:
                continue

            # Calculate duration in hours (rounded up)
            # starts_at and ends_at are already datetime objects from from_dict
            duration_hours = (session.ends_at - session.starts_at).total_seconds() / 3600
            session.session_time_units = int(ceil(duration_hours))

            parsed.append(session)

        return parsed

    def _assign_session_tags(self, sessions: List[Session]) -> List[Session]:
        """
        Groups sessions by startsAt (discrete time slots) and assigns session_1, session_2, etc. tags
        based on start time and duration.
        """
        # Sort all sessions by starts_at
        sorted_sessions = sorted(sessions, key=lambda s: s.starts_at)

        # Group by discrete time slots (rounding up to the hour)
        # A session starting at 10:50 goes into the 11:00 slot
        grouped_by_slot: Dict[int, List[Session]] = defaultdict(list)

        for session in sorted_sessions:
            # Round up to the hour: 10:00 -> slot 10, 10:01-10:59 -> slot 11
            hour = session.starts_at.hour
            minute = session.starts_at.minute

            # If there are minutes (not exactly on the hour), move to next slot
            slot_hour = hour if minute == 0 else hour + 1

            grouped_by_slot[slot_hour].append(session)

        # Sort the slots
        sorted_slots = sorted(grouped_by_slot.keys())

        # Find the first slot (smallest) to calculate base index
        first_slot = sorted_slots[0] if sorted_slots else 0

        # Assign tags based on slot index and duration
        for slot_hour in sorted_slots:
            slot_index = slot_hour - first_slot  # Index relative to first slot
            slot_sessions = grouped_by_slot[slot_hour]

            for session in slot_sessions:
                # Tag starts from session_{slot_index + 1}
                # If session lasts more than 1 hour, add multiple tags
                session_tags = []
                for i in range(session.session_time_units):
                    tag_index = slot_index + i + 1
                    session_tags.append(f"session_{tag_index}")

                session.session_tags = session_tags

        return sessions

    def _update_quizzes_with_sessions(self, sessions: List[Session]):
        """
        Updates quizzes with session tags based on session_id.
        """
        # Read all quizzes
        all_quizzes = self.quiz_repository.read_all()

        # Create mapping session_id -> session_tags
        session_mapping = {
            session.id: session.session_tags
            for session in sessions
        }

        # Update each quiz that has a matching session_id
        for quiz in all_quizzes:
            if quiz.session_id in session_mapping:
                sessions_tags = session_mapping[quiz.session_id]
                self.quiz_repository.update(
                    quiz.quiz_id,
                    {"sessions": sessions_tags}
                )

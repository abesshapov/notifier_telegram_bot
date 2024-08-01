"""Note service."""

import re
from datetime import datetime
from typing import List, Optional

import pydantic

from app.internal.repository.postgresql.notes import NoteRepository
from app.pkg.logger import get_logger
from app.pkg.models.app.notes import repository
from app.pkg.models.exceptions.repository import EmptyResult, ForeignKeyViolation


class NoteService:
    """All note-related operations are handled in that service."""

    __logger = get_logger(__name__)
    __note_repository: NoteRepository

    def __init__(self, note_repository: NoteRepository):

        self.__note_repository = note_repository

    async def get_all_notes_for_client(
        self,
        user_id: pydantic.NonNegativeInt,
    ) -> Optional[List[repository.NoteResponse]]:
        """Get all notes for client sorted by notify time."""

        try:
            return await self.__note_repository.read_for_user(
                repository.ReadNotesQueryByUserId(
                    user_id=user_id,
                ),
            )
        except EmptyResult:
            return None

    def compose_report_on_notes(
        self,
        notes: List[repository.NoteResponse],
    ) -> str:
        """Compose report for client notes."""

        report: List[str] = ["Ваши заметки:", ""]
        for i in range(len(notes)):
            report.append(f"Заметка #{i + 1}")
            report.append(notes[i].text)
            report.append(notes[i].reminder_time.strftime("%H:%M"))
            report.append("")
        return "\n".join(report)

    async def create_note(
        self,
        user_id: pydantic.NonNegativeInt,
        text: str,
        reminder_time: str,
    ) -> bool:
        """Create note with specified parameters.

        Before that, check if provided time is of correct format.
        """

        if not self.__check_if_time_is_valid(reminder_time):
            return False
        parsed_reminder_time = datetime.strptime(reminder_time, "%H:%M").time()
        try:
            await self.__note_repository.create(
                repository.CreateNoteCommand(
                    user_id=user_id,
                    reminder_time=parsed_reminder_time,
                    text=text,
                ),
            )
            return True
        except ForeignKeyViolation:
            self.__logger.error(  # pylint: disable=logging-fstring-interpolation
                f"Unexpected unregistered client: {user_id}.",
            )
            return False

    def __check_if_time_is_valid(self, time: str) -> Optional[re.Match]:
        """Check if time is of valid format which is: HH:mm."""

        pattern = r"^(?:[01]\d|2[0-3]):[0-5]\d$"
        return re.match(pattern, time)

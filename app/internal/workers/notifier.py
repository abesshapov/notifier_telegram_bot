"""Notification module.

Reminds clients of closing notes.
"""

import asyncio
from datetime import datetime, timedelta
from logging import Logger
from typing import Final

from aiogram.utils.exceptions import ChatNotFound
from pydantic import PositiveInt

from app.internal.repository.postgresql.notes import NoteRepository
from app.internal.repository.postgresql.users import UserRepository
from app.internal.workers.worker import BaseWorker
from app.pkg.clients.telegram_bot import TelegramBotClient
from app.pkg.logger import get_logger
from app.pkg.models.app.notes import repository as notes_repository
from app.pkg.models.app.users import repository as users_repository
from app.pkg.models.exceptions.repository import EmptyResult

INTERVAL_BETWEEN_JOBS: Final[PositiveInt] = 15
REMIND_WITHIN_MINUTES: Final[PositiveInt] = 10


class NotifierWorker(BaseWorker):
    """Notifier worker."""

    __logger: Logger = get_logger(__name__)
    __telegram_bot_client: TelegramBotClient
    __user_repository: UserRepository
    __note_repository: NoteRepository

    def __init__(
        self,
        telegram_bot_client: TelegramBotClient,
        user_repository: UserRepository,
        note_repository: NoteRepository,
    ):

        self.__telegram_bot_client = telegram_bot_client
        self.__user_repository = user_repository
        self.__note_repository = note_repository

    async def run(self) -> None:  # noqa: C901
        """Main function to notification worker."""

        while True:
            try:
                notes = await self.__note_repository.read_all()
                notes = [note for note in notes if not note.notified]
            except EmptyResult:
                notes = []
            self.__logger.info(  # pylint: disable=logging-fstring-interpolation
                f"Unnotified notes: {len(notes)}",
            )
            for note in notes:
                if (
                    note.reminder_time
                    < (datetime.now() + timedelta(minutes=REMIND_WITHIN_MINUTES)).time()
                ):
                    try:
                        user = await self.__user_repository.read(
                            users_repository.ReadUserQueryById(
                                id=note.user_id,
                            ),
                        )
                        await self.__telegram_bot_client.send_message(
                            user.telegram_id,
                            text=f"""
Приближается напоминание!

{note.text}
{note.reminder_time.strftime("%H:%M")}
""",
                        )
                        await self.__note_repository.update(
                            notes_repository.UpdateNoteNotifiedStateCommand(
                                id=note.id,
                                notified=True,
                            ),
                        )
                        self.__logger.info(  # pylint: disable=logging-fstring-interpolation, line-too-long
                            f"Successfully notified client on note {note.id}.",
                        )
                    except EmptyResult:
                        self.__logger.error(  # pylint: disable=logging-fstring-interpolation, line-too-long
                            f"Apparantely, user {note.user_id} is no longer existent.",
                        )
                    except ChatNotFound:
                        self.__logger.error(  # pylint: disable=logging-fstring-interpolation, line-too-long
                            f"Chat for user {user.telegram_id} does not longer exist.",
                        )
                    except Exception as ex:  # pylint: disable=broad-exception-caught
                        self.__logger.error(  # pylint: disable=logging-fstring-interpolation, line-too-long
                            f"Unexpected error was raised when trying to notify: {ex}.",
                        )
            await asyncio.sleep(INTERVAL_BETWEEN_JOBS)

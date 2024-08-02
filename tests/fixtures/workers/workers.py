"""Workers fixtures."""

import pytest

from app.internal.repository.postgresql.notes import NoteRepository
from app.internal.repository.postgresql.users import UserRepository
from app.internal.workers.notifier import NotifierWorker
from app.pkg.clients.telegram_bot.client import TelegramBotClient


@pytest.fixture
def notifier_worker(
    telegram_bot_client: TelegramBotClient,
    user_repository: UserRepository,
    note_repository: NoteRepository,
) -> NotifierWorker:
    """Notifier worker fixture."""

    return NotifierWorker(
        telegram_bot_client=telegram_bot_client,
        user_repository=user_repository,
        note_repository=note_repository,
    )

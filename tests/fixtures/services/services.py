"""Fixtures for services."""

import pytest

from app.internal.repository.postgresql.notes import NoteRepository
from app.internal.repository.postgresql.users import UserRepository
from app.internal.services.note import NoteService
from app.internal.services.telegram import TelegramService
from app.internal.services.user import UserService
from app.pkg.clients.telegram_bot.client import TelegramBotClient
from app.pkg.settings import settings


@pytest.fixture
def note_service(
    note_repository: NoteRepository,
) -> NoteService:
    """Note service fixture."""

    return NoteService(
        note_repository=note_repository,
    )


@pytest.fixture
def user_service(
    user_repository: UserRepository,
) -> UserService:
    """User service fixture."""

    return UserService(
        user_repository=user_repository,
    )


@pytest.fixture
def telegram_service(
    telegram_bot_client: TelegramBotClient,
    user_service: UserService,  # pylint: disable=redefined-outer-name
    note_service: NoteService,  # pylint: disable=redefined-outer-name
) -> TelegramService:
    """Telegram service fixture."""

    return TelegramService(
        telegram_bot_client=telegram_bot_client,
        webhook_url=settings.TELEGRAM.WEBHOOK_URL,
        user_service=user_service,
        note_service=note_service,
    )

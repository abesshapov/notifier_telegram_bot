"""Client fixtures for tests."""

import pytest

from app.pkg.clients.telegram_bot import TelegramBotClient
from app.pkg.settings.settings import Settings


@pytest.fixture
def telegram_bot_client() -> TelegramBotClient:
    """Telegram bot client fixture."""

    return TelegramBotClient(
        token=Settings.TELEGRAM.TOKEN,
    )

"""Clients module."""

from dependency_injector import containers, providers

from app.pkg.clients.telegram_bot import TelegramBotClient
from app.pkg.settings import settings
from app.pkg.settings.settings import Settings


class Clients(containers.DeclarativeContainer):
    """Containers with clients."""

    configuration: Settings = providers.Configuration(
        name="settings",
        pydantic_settings=[settings],
    )

    telegram_bot_client = providers.Singleton(
        TelegramBotClient,
        token=configuration.TELEGRAM.TOKEN,
    )

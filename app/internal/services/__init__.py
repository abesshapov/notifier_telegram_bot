"""Service layer."""

from dependency_injector import containers, providers

from app.internal.repository import Repositories, postgresql
from app.internal.services.telegram import TelegramService
from app.pkg.clients import Clients
from app.pkg.settings import settings
from app.pkg.settings.settings import Settings


class Services(containers.DeclarativeContainer):
    """Containers with services."""

    configuration: Settings = providers.Configuration(
        name="settings",
        pydantic_settings=[settings],
    )

    repositories: postgresql.Repositories = providers.Container(Repositories.postgres)

    clients: Clients = providers.Container(Clients)

    # Services
    telegram_service = providers.Singleton(
        TelegramService,
        telegram_bot_client=clients.telegram_bot_client,
        webhook_url=configuration.TELEGRAM.WEBHOOK_URL,
    )

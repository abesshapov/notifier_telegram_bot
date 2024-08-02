"""Workers package."""

from dependency_injector import containers, providers

from app.internal.repository import Repositories, postgresql
from app.internal.services import Services
from app.internal.workers.notifier import NotifierWorker
from app.pkg.clients import Clients


class Workers(containers.DeclarativeContainer):
    """Workers container."""

    clients: Clients = providers.Container(Clients)

    services: Services = providers.Container(Services)

    repositories: postgresql.Repositories = providers.Container(Repositories.postgres)

    notifier_worker: NotifierWorker = providers.Singleton(
        NotifierWorker,
        telegram_bot_client=clients.telegram_bot_client,
        user_repository=repositories.users_repository,
        note_repository=repositories.notes_repository,
    )

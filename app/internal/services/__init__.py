"""Service layer."""

from dependency_injector import containers, providers

from app.internal.repository import Repositories, postgresql
from app.pkg.clients import Clients


class Services(containers.DeclarativeContainer):
    """Containers with services."""

    repositories: postgresql.Repositories = providers.Container(Repositories.postgres)

    clients: Clients = providers.Container(Clients)

    # Services

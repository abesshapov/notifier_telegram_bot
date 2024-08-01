"""Workers package."""

from dependency_injector import containers, providers

from app.internal.services import Services
from app.pkg.clients import Clients


class Workers(containers.DeclarativeContainer):
    """Workers container."""

    clients: Clients = providers.Container(Clients)

    services: Services = providers.Container(Services)

"""Clients module."""

from dependency_injector import containers, providers

from app.pkg.settings import settings


class Clients(containers.DeclarativeContainer):
    """Containers with clients."""

    configuration = providers.Configuration(
        name="settings",
        pydantic_settings=[settings],
    )

"""All postgresql repositories are defined here."""

from dependency_injector import containers, providers


class Repositories(containers.DeclarativeContainer):
    """Container for postgresql repositories."""

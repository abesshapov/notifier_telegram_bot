"""All postgresql repositories are defined here."""

from dependency_injector import containers, providers
from app.internal.repository.postgresql.notes import NoteRepository
from app.internal.repository.postgresql.users import UserRepository


class Repositories(containers.DeclarativeContainer):
    """Container for postgresql repositories."""

    notes_repository: NoteRepository = providers.Singleton(
        NoteRepository,
    )
    users_repository: UserRepository = providers.Singleton(
        UserRepository,
    )

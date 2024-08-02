"""All fixtures for postgresql repositories."""

import pytest

from app.internal.repository.postgresql.notes import NoteRepository
from app.internal.repository.postgresql.users import UserRepository


@pytest.fixture
def note_repository() -> NoteRepository:
    return NoteRepository()


@pytest.fixture
def user_repository() -> UserRepository:
    return UserRepository()

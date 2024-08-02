"""Tests on notify worker."""

import time
from datetime import datetime, timedelta
from typing import Final

import pytest

from app.internal.repository.postgresql.notes import NoteRepository
from app.internal.repository.postgresql.users import UserRepository
from app.internal.workers.notifier import REMIND_WITHIN_MINUTES, NotifierWorker
from app.pkg.models.app.notes import repository as notes_repository
from app.pkg.models.app.users import repository as users_repository
from app.pkg.models.exceptions.repository import EmptyResult

POSTPONE_NOTE_BY: Final[int] = 5


@pytest.fixture
async def delete_notes(
    note_repository: NoteRepository,
) -> None:
    """Delete notes fixture."""

    try:
        notes = await note_repository.read_all()
        for note in notes:
            await note_repository.delete(
                notes_repository.DeleteNoteCommand(
                    id=note.id,
                ),
            )
    except EmptyResult:
        pass


@pytest.fixture
async def create_user(
    user_repository: UserRepository,
    specific_client_id: int,
) -> int:
    """Create user fixture."""

    try:
        user = await user_repository.read(
            users_repository.ReadUserQueryByTelegramId(
                telegram_id=specific_client_id,
            ),
        )
        return user.id
    except EmptyResult:
        return (
            await user_repository.create(
                users_repository.CreateUserCommand(
                    telegram_id=specific_client_id,
                    email="test@mail.ru",
                    name="Alex",
                ),
            )
        ).id


@pytest.fixture
async def create_notified_note(
    note_repository: NoteRepository,
    delete_notes: None,  # pylint: disable=redefined-outer-name, unused-argument
    create_user: int,  # pylint: disable=redefined-outer-name
) -> notes_repository.NoteResponse:
    """Create notified note."""

    note = await note_repository.create(
        notes_repository.CreateNoteCommand(
            user_id=create_user,
            reminder_time=datetime.now().time(),
            text="Some note text",
        ),
    )
    return await note_repository.update(
        notes_repository.UpdateNoteNotifiedStateCommand(
            notified=True,
            id=note.id,
        ),
    )


@pytest.fixture
async def create_unnotified_note(
    note_repository: NoteRepository,
    delete_notes: None,  # pylint: disable=redefined-outer-name, unused-argument
    create_user: int,  # pylint: disable=redefined-outer-name
) -> notes_repository.NoteResponse:
    """Create notified note."""

    return await note_repository.create(
        notes_repository.CreateNoteCommand(
            user_id=create_user,
            reminder_time=(
                datetime.now()
                + timedelta(seconds=REMIND_WITHIN_MINUTES * 60 + POSTPONE_NOTE_BY)
            ).time(),
            text="Some note text",
        ),
    )


async def test_notify_worker_on_empty_notes(
    notifier_worker: NotifierWorker,
    delete_notes: None,  # pylint: disable=redefined-outer-name, unused-argument
):
    """Test notify worker work on empty notes."""

    assert not await notifier_worker.inner_function()


async def test_notify_worker_on_empty_unnotified_notes(
    notifier_worker: NotifierWorker,
    create_notified_note: notes_repository.NoteResponse,  # pylint: disable=redefined-outer-name, unused-argument, line-too-long
):
    """Test notify worker work on empty unnotified notes."""

    assert not await notifier_worker.inner_function()


async def test_notify_worker_on_awaiting_notes(
    notifier_worker: NotifierWorker,
    create_unnotified_note: notes_repository.NoteResponse,  # pylint: disable=redefined-outer-name, unused-argument, line-too-long
):
    """Test notify worker work on notes, that are not yet to be notified."""

    time.sleep(POSTPONE_NOTE_BY / 2)
    assert not await notifier_worker.inner_function()


async def test_notify_worker_on_read_note(
    notifier_worker: NotifierWorker,
    note_repository: NoteRepository,
    user_repository: UserRepository,
    create_unnotified_note: notes_repository.NoteResponse,  # pylint: disable=redefined-outer-name, line-too-long
):
    """Test notify worker work on notes, that have to be notified."""

    time.sleep(POSTPONE_NOTE_BY + 1)
    result = await notifier_worker.inner_function()
    assert len(result) == 1
    message = result[0]
    assert (
        message.text
        == f"""Приближается напоминание!

{create_unnotified_note.text}
{create_unnotified_note.reminder_time.strftime("%H:%M")}"""
    )

    user = await user_repository.read(
        users_repository.ReadUserQueryById(id=create_unnotified_note.user_id),
    )
    assert message.chat.id == user.telegram_id

    eventual_note = await note_repository.read(
        notes_repository.ReadNoteQueryById(id=create_unnotified_note.id),
    )
    assert eventual_note.to_dict() == create_unnotified_note.to_dict() | {
        "notified": True,
    }

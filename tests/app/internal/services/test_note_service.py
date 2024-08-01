"""Tests on note service."""

from datetime import datetime, timedelta

import pytest

from app.internal.repository.postgresql.notes import NoteRepository
from app.internal.repository.postgresql.users import UserRepository
from app.internal.services.note import NoteService
from app.pkg.models.app.notes import repository as notes_repository
from app.pkg.models.app.users import repository as users_repository
from app.pkg.models.exceptions.repository import EmptyResult


@pytest.mark.parametrize("existent", [True, False])
async def test_get_notes_for_client(
    note_service: NoteService,
    note_repository: NoteRepository,
    user_repository: UserRepository,
    client_id: int,
    existent: bool,
):
    """Test on getting notes for client."""

    user = await user_repository.create(
        users_repository.CreateUserCommand(
            telegram_id=client_id,
            email="test@mail.ru",
            name="Peter",
        ),
    )
    notes = None
    if existent:
        notes = []
        for i in range(3):
            notes.append(
                await note_repository.create(
                    notes_repository.CreateNoteCommand(
                        user_id=user.id,
                        reminder_time=(datetime.now() + timedelta(minutes=i)).time(),
                        text=f"Note #{i + 1}",
                    ),
                ),
            )

    assert notes == await note_service.get_all_notes_for_client(user.id)


async def test_compose_report_on_notes(
    note_service: NoteService,
    note_repository: NoteRepository,
    user_repository: UserRepository,
    client_id: int,
):
    """Test on report compose on notes."""

    user = await user_repository.create(
        users_repository.CreateUserCommand(
            telegram_id=client_id,
            email="test@mail.ru",
            name="Peter",
        ),
    )
    reminder_time = datetime.now()
    notes = []
    for i in range(2):
        notes.append(
            await note_repository.create(
                notes_repository.CreateNoteCommand(
                    user_id=user.id,
                    reminder_time=(reminder_time + timedelta(minutes=i)).time(),
                    text=f"Note #{i + 1}",
                ),
            ),
        )

    expected_report = f"""Ваши заметки:

Заметка #1
Note #1
{reminder_time.time().strftime("%H:%M")}

Заметка #2
Note #2
{(reminder_time + timedelta(minutes=1)).time().strftime("%H:%M")}
"""

    assert expected_report == note_service.compose_report_on_notes(notes)


@pytest.mark.parametrize(
    "time_valid",
    [
        (True, "00:30"),
        (False, "0:30"),
        (False, "00:3"),
        (False, "invalid"),
        (False, "25:30"),
        (False, "10:60"),
    ],
)
async def test_on_note_creation(
    note_service: NoteService,
    note_repository: NoteRepository,
    user_repository: UserRepository,
    client_id: int,
    time_valid: tuple,
):
    """Test on note creation."""

    user = await user_repository.create(
        users_repository.CreateUserCommand(
            telegram_id=client_id,
            email="test@mail.ru",
            name="Peter",
        ),
    )
    time = time_valid[1]

    assert time_valid[0] == await note_service.create_note(
        user.id,
        "Some note text",
        time,
    )

    if time_valid[0]:
        user_notes = await note_repository.read_for_user(
            notes_repository.ReadNotesQueryByUserId(
                user_id=user.id,
            ),
        )
        assert user_notes
        assert len(user_notes) == 1
        user_note = user_notes[0]
        assert user_note.text == "Some note text"
        assert not user_note.notified
        assert user_note.reminder_time.strftime("%H:%M") == time_valid[1]
    else:
        with pytest.raises(EmptyResult):
            await note_repository.read_for_user(
                notes_repository.ReadNotesQueryByUserId(
                    user_id=user.id,
                ),
            )


async def test_note_creation_for_nonexistent_client(
    note_service: NoteService,
    client_id: int,
):
    """Test on note creation for nonexistent client."""

    assert not await note_service.create_note(
        client_id,
        "Some note text",
        "00:30",
    )

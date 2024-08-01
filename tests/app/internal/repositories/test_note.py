"""Tests on note repository."""

from datetime import datetime, timedelta
from typing import List

import pytest

from app.internal.repository.postgresql.notes import NoteRepository
from app.internal.repository.postgresql.users import UserRepository
from app.pkg.models.app.notes import repository as notes_repository
from app.pkg.models.app.users import repository as users_repository
from app.pkg.models.exceptions.repository import EmptyResult, ForeignKeyViolation


async def test_note_creation_for_nonexistent_user(
    note_repository: NoteRepository,
    client_id: int,
):
    """Test on note creation, that violates foreigh key constraint."""

    with pytest.raises(ForeignKeyViolation):
        await note_repository.create(
            notes_repository.CreateNoteCommand(
                user_id=client_id,
                reminder_time=datetime.now().time(),
                text="Some reminder",
            ),
        )


async def test_note_creation_for_existent_user(
    note_repository: NoteRepository,
    user_repository: UserRepository,
    client_id: int,
):
    """Test on note creation for user."""

    user = await user_repository.create(
        users_repository.CreateUserCommand(
            telegram_id=client_id,
            email="some@email",
            name="Peter",
        ),
    )

    reminder_time = datetime.now().time()
    creation_response = await note_repository.create(
        notes_repository.CreateNoteCommand(
            user_id=user.id,
            reminder_time=reminder_time,
            text="Some reminder",
        ),
    )
    assert creation_response.user_id == user.id
    assert creation_response.reminder_time == reminder_time
    assert creation_response.text == "Some reminder"
    assert not creation_response.notified


async def test_multiple_notes_creation_for_user(
    note_repository: NoteRepository,
    user_repository: UserRepository,
    client_id: int,
):
    """Test on multiple notes creation for user."""

    user = await user_repository.create(
        users_repository.CreateUserCommand(
            telegram_id=client_id,
            email="some@email",
            name="Peter",
        ),
    )

    reminder_time = datetime.now().time()
    creation_response = await note_repository.create(
        notes_repository.CreateNoteCommand(
            user_id=user.id,
            reminder_time=reminder_time,
            text="Some reminder",
        ),
    )

    another_creation_response = await note_repository.create(
        notes_repository.CreateNoteCommand(
            user_id=user.id,
            reminder_time=reminder_time,
            text="Some reminder",
        ),
    )
    assert another_creation_response.to_dict() == creation_response.to_dict() | {
        "id": creation_response.id + 1,
    }, "Id of the note should be more than previous ones by one."


async def test_specific_note_reading(
    note_repository: NoteRepository,
    user_repository: UserRepository,
    client_id: int,
):
    """Test on specific note reading."""

    user = await user_repository.create(
        users_repository.CreateUserCommand(
            telegram_id=client_id,
            email="some@email",
            name="Peter",
        ),
    )

    creation_response = await note_repository.create(
        notes_repository.CreateNoteCommand(
            user_id=user.id,
            reminder_time=datetime.now().time(),
            text="Some reminder",
        ),
    )

    read_response = await note_repository.read(
        notes_repository.ReadNoteQueryById(
            id=creation_response.id,
        ),
    )
    assert read_response == creation_response


async def test_user_notes_reading(
    note_repository: NoteRepository,
    user_repository: UserRepository,
    client_id: int,
):
    """Test on user notes reading."""

    user = await user_repository.create(
        users_repository.CreateUserCommand(
            telegram_id=client_id,
            email="some@email",
            name="Peter",
        ),
    )

    created_notes: List[notes_repository.NoteResponse] = []
    for i in range(3):
        created_notes.append(
            await note_repository.create(
                notes_repository.CreateNoteCommand(
                    user_id=user.id,
                    reminder_time=(datetime.now() + timedelta(hours=i)).time(),
                    text="Some reminder",
                ),
            ),
        )

    user_notes = await note_repository.read_for_user(
        notes_repository.ReadNotesQueryByUserId(
            user_id=user.id,
        ),
    )
    assert created_notes == user_notes


async def test_on_all_notes_reading(
    note_repository: NoteRepository,
    user_repository: UserRepository,
    client_id: int,
):
    """Test on all notes reading."""

    try:
        initial_notes = await note_repository.read_all()
    except EmptyResult:
        initial_notes = []

    user = await user_repository.create(
        users_repository.CreateUserCommand(
            telegram_id=client_id,
            email="some@email",
            name="Peter",
        ),
    )

    creation_response = await note_repository.create(
        notes_repository.CreateNoteCommand(
            user_id=user.id,
            reminder_time=datetime.now().time(),
            text="Some reminder",
        ),
    )

    eventual_notes = await note_repository.read_all()
    assert creation_response in eventual_notes
    assert len(eventual_notes) == len(initial_notes) + 1


async def test_on_note_notified_state_update(
    note_repository: NoteRepository,
    user_repository: UserRepository,
    client_id: int,
):
    """Test on note notified state update."""

    user = await user_repository.create(
        users_repository.CreateUserCommand(
            telegram_id=client_id,
            email="some@email",
            name="Peter",
        ),
    )

    creation_response = await note_repository.create(
        notes_repository.CreateNoteCommand(
            user_id=user.id,
            reminder_time=datetime.now().time(),
            text="Some reminder",
        ),
    )

    update_response = await note_repository.update(
        notes_repository.UpdateNoteNotifiedStateCommand(
            notified=True,
            id=creation_response.id,
        ),
    )
    assert creation_response.to_dict() | {"notified": True} == update_response.to_dict()


async def test_on_note_deletion(
    note_repository: NoteRepository,
    user_repository: UserRepository,
    client_id: int,
):
    """Test on note deletion."""

    user = await user_repository.create(
        users_repository.CreateUserCommand(
            telegram_id=client_id,
            email="some@email",
            name="Peter",
        ),
    )

    creation_response = await note_repository.create(
        notes_repository.CreateNoteCommand(
            user_id=user.id,
            reminder_time=datetime.now().time(),
            text="Some reminder",
        ),
    )

    deletion_response = await note_repository.delete(
        notes_repository.DeleteNoteCommand(
            id=creation_response.id,
        ),
    )
    assert creation_response == deletion_response

    with pytest.raises(EmptyResult):
        await note_repository.read(
            notes_repository.ReadNoteQueryById(
                id=creation_response.id,
            ),
        )

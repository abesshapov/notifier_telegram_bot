"""Test on telegram service."""

from datetime import datetime

import pytest
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext

from app.internal.repository.postgresql.notes import NoteRepository
from app.internal.repository.postgresql.users import UserRepository
from app.internal.services.telegram import States, TelegramService
from app.pkg.models.app.notes import repository as notes_repository
from app.pkg.models.app.users import repository as users_repository
from app.pkg.models.exceptions.repository import EmptyResult


@pytest.fixture
async def delete_user(
    user_repository: UserRepository,
    specific_client_id: int,
) -> None:
    """Delete user fixture."""

    try:
        user = await user_repository.read(
            users_repository.ReadUserQueryByTelegramId(
                telegram_id=specific_client_id,
            ),
        )
        await user_repository.delete(
            users_repository.DeleteUserCommand(
                id=user.id,
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
async def delete_notes(
    create_user: int,  # pylint: disable=redefined-outer-name
    note_repository: NoteRepository,
) -> int:
    """Delete notes fixture."""

    try:
        notes = await note_repository.read_for_user(
            notes_repository.ReadNotesQueryByUserId(
                user_id=create_user,
            ),
        )
        for note in notes:
            await note_repository.delete(
                notes_repository.DeleteNoteCommand(
                    id=note.id,
                ),
            )
    except EmptyResult:
        pass
    return create_user


@pytest.fixture
async def create_note(
    delete_notes: int,  # pylint: disable=redefined-outer-name
    note_repository: NoteRepository,
) -> notes_repository.NoteResponse:
    """Create note fixture."""

    return await note_repository.create(
        notes_repository.CreateNoteCommand(
            user_id=delete_notes,
            text="Some note text",
            reminder_time=datetime.now().time(),
        ),
    )


async def test_new_user_register(
    telegram_service: TelegramService,
    delete_user: None,  # pylint: disable=redefined-outer-name, unused-argument
    specific_client_id: int,
):
    """Test on new user registration."""

    Dispatcher.set_current(telegram_service.get_dispatcher())
    Bot.set_current(telegram_service.get_bot())
    message = await telegram_service.on_start_command(
        types.Message(
            chat=types.Chat(id=specific_client_id),
            text="/start",
        ),
        FSMContext(
            telegram_service.get_dispatcher().storage,
            chat=specific_client_id,
            user=specific_client_id,
        ),
    )
    assert (
        message.text
        == """Чтобы продолжить пользоваться ботом, нужно пройти регистрацию.
Введите имя пользователя:"""
    )
    assert message.chat.id == specific_client_id

    state = await telegram_service.get_dispatcher().storage.get_state(
        chat=specific_client_id,
        user=specific_client_id,
    )
    assert state == States.AWAITING_USERNAME


async def test_registration_for_existent_user(
    telegram_service: TelegramService,
    create_user: int,  # pylint: disable=redefined-outer-name, unused-argument
    specific_client_id: int,
):
    """Test on registration attempt for existent user."""

    Dispatcher.set_current(telegram_service.get_dispatcher())
    Bot.set_current(telegram_service.get_bot())
    message = await telegram_service.on_start_command(
        types.Message(
            chat=types.Chat(id=specific_client_id),
            text="/start",
        ),
        FSMContext(
            telegram_service.get_dispatcher().storage,
            chat=specific_client_id,
            user=specific_client_id,
        ),
    )
    assert message.text == "Вы уже зарегистрированы."
    assert message.chat.id == specific_client_id

    state = await telegram_service.get_dispatcher().storage.get_state(
        chat=specific_client_id,
        user=specific_client_id,
    )
    assert not state


async def test_new_username_processing(
    telegram_service: TelegramService,
    delete_user: None,  # pylint: disable=redefined-outer-name, unused-argument
    specific_client_id: int,
):
    """Test on new username processing."""

    username = "Alex"
    state = FSMContext(
        telegram_service.get_dispatcher().storage,
        chat=specific_client_id,
        user=specific_client_id,
    )
    await telegram_service.get_dispatcher().storage.set_state(
        chat=specific_client_id,
        user=specific_client_id,
        state=States.AWAITING_USERNAME,
    )
    Dispatcher.set_current(telegram_service.get_dispatcher())
    Bot.set_current(telegram_service.get_bot())
    message = await telegram_service.process_username(
        types.Message(
            chat=types.Chat(id=specific_client_id),
            text=username,
        ),
        state,
    )
    assert (
        message.text
        == f"""Ваше новое имя пользователя: {username}.
Введите email:"""
    )
    assert message.chat.id == specific_client_id

    current_state = await telegram_service.get_dispatcher().storage.get_state(
        chat=specific_client_id,
        user=specific_client_id,
    )
    assert current_state == States.AWAITING_EMAIL
    assert (await state.get_data()).get(States.AWAITING_USERNAME) == username


@pytest.mark.parametrize("valid_email", [True, False])
async def test_new_email_processing(
    telegram_service: TelegramService,
    user_repository: UserRepository,
    delete_user: None,  # pylint: disable=redefined-outer-name, unused-argument
    specific_client_id: int,
    valid_email: bool,
):
    """Test on new email processing."""

    username = "Alex"
    email = "test@mail.ru" if valid_email else "invalid"
    state = FSMContext(
        telegram_service.get_dispatcher().storage,
        chat=specific_client_id,
        user=specific_client_id,
    )
    await telegram_service.get_dispatcher().storage.set_state(
        chat=specific_client_id,
        user=specific_client_id,
        state=States.AWAITING_EMAIL,
    )
    await telegram_service.get_dispatcher().storage.set_data(
        chat=specific_client_id,
        user=specific_client_id,
        data={
            States.AWAITING_USERNAME: username,
        },
    )
    Dispatcher.set_current(telegram_service.get_dispatcher())
    Bot.set_current(telegram_service.get_bot())
    message = await telegram_service.process_email(
        types.Message(
            chat=types.Chat(id=specific_client_id),
            text=email,
        ),
        state,
    )
    assert message.text == (
        "Вы успешно прошли регистрацию! Теперь вам доступен весь функционал."
        if valid_email
        else "Введен некорректный email. Попробуйте еще раз:"
    )
    assert message.chat.id == specific_client_id

    current_state = await telegram_service.get_dispatcher().storage.get_state(
        chat=specific_client_id,
        user=specific_client_id,
    )
    assert current_state == (None if valid_email else States.AWAITING_EMAIL)

    if valid_email:
        user = await user_repository.read(
            users_repository.ReadUserQueryByTelegramId(telegram_id=specific_client_id),
        )
        assert user.name == username
        assert user.email == email
    else:
        with pytest.raises(EmptyResult):
            await user_repository.read(
                users_repository.ReadUserQueryByTelegramId(
                    telegram_id=specific_client_id,
                ),
            )


async def test_my_notes_command_processing_for_unregistered(
    telegram_service: TelegramService,
    delete_user: None,  # pylint: disable=redefined-outer-name, unused-argument
    specific_client_id: int,
):
    """Test on my notes processing for unregistered client."""

    Dispatcher.set_current(telegram_service.get_dispatcher())
    Bot.set_current(telegram_service.get_bot())
    message = await telegram_service.on_my_notes_command(
        types.Message(
            chat=types.Chat(id=specific_client_id),
            text="/mynotes",
        ),
        FSMContext(
            telegram_service.get_dispatcher().storage,
            chat=specific_client_id,
            user=specific_client_id,
        ),
    )
    assert (
        message.text
        == "Перед тем как использовать эту функцию, вам необходимо пройти регистрацию."
    )
    assert message.chat.id == specific_client_id

    state = await telegram_service.get_dispatcher().storage.get_state(
        chat=specific_client_id,
        user=specific_client_id,
    )
    assert not state


async def test_add_note_command_processing_for_unregistered(
    telegram_service: TelegramService,
    delete_user: None,  # pylint: disable=redefined-outer-name, unused-argument
    specific_client_id: int,
):
    """Test on add note processing for unregistered client."""

    Dispatcher.set_current(telegram_service.get_dispatcher())
    Bot.set_current(telegram_service.get_bot())
    message = await telegram_service.on_add_note_command(
        types.Message(
            chat=types.Chat(id=specific_client_id),
            text="/addnote",
        ),
        FSMContext(
            telegram_service.get_dispatcher().storage,
            chat=specific_client_id,
            user=specific_client_id,
        ),
    )
    assert (
        message.text
        == "Перед тем как использовать эту функцию, вам необходимо пройти регистрацию."
    )
    assert message.chat.id == specific_client_id

    state = await telegram_service.get_dispatcher().storage.get_state(
        chat=specific_client_id,
        user=specific_client_id,
    )
    assert not state


async def test_on_my_notes_command_processing_for_registered_with_notes(
    telegram_service: TelegramService,
    create_note: notes_repository.NoteResponse,  # pylint: disable=redefined-outer-name
    specific_client_id: int,
):
    """Test on my notes processing for registered user with a note."""

    Dispatcher.set_current(telegram_service.get_dispatcher())
    Bot.set_current(telegram_service.get_bot())
    message = await telegram_service.on_my_notes_command(
        types.Message(
            chat=types.Chat(id=specific_client_id),
            text="/mynotes",
        ),
        FSMContext(
            telegram_service.get_dispatcher().storage,
            chat=specific_client_id,
            user=specific_client_id,
        ),
    )
    assert (
        message.text
        == f"""Ваши заметки:

Заметка #1
{create_note.text}
{create_note.reminder_time.strftime("%H:%M")}"""
    )
    assert message.chat.id == specific_client_id

    state = await telegram_service.get_dispatcher().storage.get_state(
        chat=specific_client_id,
        user=specific_client_id,
    )
    assert not state


async def test_on_my_notes_command_processing_for_registered_without_notes(
    telegram_service: TelegramService,
    delete_notes: int,  # pylint: disable=unused-argument, redefined-outer-name
    specific_client_id: int,
):
    """Test on my notes processing for registered user without notes."""

    Dispatcher.set_current(telegram_service.get_dispatcher())
    Bot.set_current(telegram_service.get_bot())
    message = await telegram_service.on_my_notes_command(
        types.Message(
            chat=types.Chat(id=specific_client_id),
            text="/mynotes",
        ),
        FSMContext(
            telegram_service.get_dispatcher().storage,
            chat=specific_client_id,
            user=specific_client_id,
        ),
    )
    assert message.text == "У вас еще нет заметок."
    assert message.chat.id == specific_client_id

    state = await telegram_service.get_dispatcher().storage.get_state(
        chat=specific_client_id,
        user=specific_client_id,
    )
    assert not state


async def test_on_add_note_for_registered_user(
    telegram_service: TelegramService,
    create_user: int,  # pylint: disable=redefined-outer-name, unused-argument
    specific_client_id: int,
):
    """Test on add note processing for registered user."""

    Dispatcher.set_current(telegram_service.get_dispatcher())
    Bot.set_current(telegram_service.get_bot())
    message = await telegram_service.on_add_note_command(
        types.Message(
            chat=types.Chat(id=specific_client_id),
            text="/addnote",
        ),
        FSMContext(
            telegram_service.get_dispatcher().storage,
            chat=specific_client_id,
            user=specific_client_id,
        ),
    )
    assert message.text == "Введите текст для новой заметки:"
    assert message.chat.id == specific_client_id

    state = await telegram_service.get_dispatcher().storage.get_state(
        chat=specific_client_id,
        user=specific_client_id,
    )
    assert state == States.AWAITING_NOTE_TEXT


async def test_new_note_text_processing(
    telegram_service: TelegramService,
    create_user: int,  # pylint: disable=redefined-outer-name, unused-argument
    specific_client_id: int,
):
    """Test on new note text processing."""

    text = "Some note text"
    state = FSMContext(
        telegram_service.get_dispatcher().storage,
        chat=specific_client_id,
        user=specific_client_id,
    )
    await telegram_service.get_dispatcher().storage.set_state(
        chat=specific_client_id,
        user=specific_client_id,
        state=States.AWAITING_NOTE_TEXT,
    )
    Dispatcher.set_current(telegram_service.get_dispatcher())
    Bot.set_current(telegram_service.get_bot())
    message = await telegram_service.process_note_text(
        types.Message(
            chat=types.Chat(id=specific_client_id),
            text=text,
        ),
        state,
    )
    assert message.text == "Введите время напоминания в формате HH:mm:"
    assert message.chat.id == specific_client_id

    current_state = await telegram_service.get_dispatcher().storage.get_state(
        chat=specific_client_id,
        user=specific_client_id,
    )
    assert current_state == States.AWAITING_NOTE_REMINDER_TIME
    assert (await state.get_data()).get(States.AWAITING_NOTE_TEXT) == text


@pytest.mark.parametrize("valid_time", [True, False])
async def test_new_note_remainder_time_processing(
    telegram_service: TelegramService,
    note_repository: NoteRepository,
    delete_notes: int,  # pylint: disable=redefined-outer-name
    specific_client_id: int,
    valid_time: bool,
):
    """Test on new note reminder time processing."""

    text = "Some note text"
    time = "00:30" if valid_time else "invalid"
    state = FSMContext(
        telegram_service.get_dispatcher().storage,
        chat=specific_client_id,
        user=specific_client_id,
    )
    await telegram_service.get_dispatcher().storage.set_state(
        chat=specific_client_id,
        user=specific_client_id,
        state=States.AWAITING_NOTE_REMINDER_TIME,
    )
    await telegram_service.get_dispatcher().storage.set_data(
        chat=specific_client_id,
        user=specific_client_id,
        data={
            States.AWAITING_NOTE_TEXT: text,
        },
    )
    Dispatcher.set_current(telegram_service.get_dispatcher())
    Bot.set_current(telegram_service.get_bot())
    message = await telegram_service.process_reminder_time(
        types.Message(
            chat=types.Chat(id=specific_client_id),
            text=time,
        ),
        state,
    )
    assert message.text == (
        "Вы успешно создали новую заметку!"
        if valid_time
        else "Некорректный формат времени уведомления. Попробуйте еще раз:"
    )
    assert message.chat.id == specific_client_id

    current_state = await telegram_service.get_dispatcher().storage.get_state(
        chat=specific_client_id,
        user=specific_client_id,
    )
    assert current_state == (None if valid_time else States.AWAITING_NOTE_REMINDER_TIME)

    if valid_time:
        note = await note_repository.read_for_user(
            notes_repository.ReadNotesQueryByUserId(
                user_id=delete_notes,
            ),
        )
        assert len(note) == 1
        note = note[0]
        assert note.text == text
        assert note.reminder_time.strftime("%H:%M") == time
        assert not note.notified
    else:
        with pytest.raises(EmptyResult):
            await note_repository.read_for_user(
                notes_repository.ReadNotesQueryByUserId(
                    user_id=delete_notes,
                ),
            )

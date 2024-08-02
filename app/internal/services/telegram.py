"""Telegram service."""


from enum import Enum

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

from app.internal.services.note import NoteService
from app.internal.services.user import UserService
from app.pkg.clients import TelegramBotClient
from app.pkg.logger import get_logger


class States(Enum):
    """State machine on clients transitions between stages."""

    AWAITING_USERNAME = 1
    AWAITING_EMAIL = 2
    AWAITING_NOTE_TEXT = 3
    AWAITING_NOTE_REMINDER_TIME = 4


class TelegramService:
    """Contains all handlers for Telegram Bot.

    New clients requests are being processed in it.
    """

    __logger = get_logger(__name__)
    __webhook_url: str
    __telegram_bot_client: TelegramBotClient
    __dp: Dispatcher
    __user_service: UserService
    __note_service: NoteService

    def __init__(
        self,
        telegram_bot_client: TelegramBotClient,
        webhook_url: str,
        user_service: UserService,
        note_service: NoteService,
    ):

        self.__webhook_url = webhook_url
        self.__telegram_bot_client = telegram_bot_client
        self.__dp = Dispatcher(telegram_bot_client.get_bot(), storage=MemoryStorage())
        self.__user_service = user_service
        self.__note_service = note_service
        self.__register_handlers()

    async def on_start_command(
        self,
        msg: types.Message,
        state: FSMContext,
    ) -> types.Message:
        """Process start command."""

        await state.finish()
        client_id = msg.from_user.id if msg.from_user else msg.chat.id
        user_existent = await self.__user_service.check_if_user_existent_for_client(
            client_id,
        )
        if user_existent:
            return await msg.answer("Вы уже зарегистрированы.")
        else:
            await self.__dp.storage.set_state(
                chat=msg.chat.id,
                user=client_id,
                state=States.AWAITING_USERNAME,
            )
            return await msg.answer(
                """
Чтобы продолжить пользоваться ботом, нужно пройти регистрацию.
Введите имя пользователя:
                """,
            )

    async def process_username(
        self,
        msg: types.Message,
        state: FSMContext,
    ) -> types.Message:
        """Process new user name."""

        client_id = msg.from_user.id if msg.from_user else msg.chat.id
        await state.update_data(
            {
                States.AWAITING_USERNAME: msg.text,
            },
        )
        await self.__dp.storage.set_state(
            chat=msg.chat.id,
            user=client_id,
            state=States.AWAITING_EMAIL,
        )
        return await msg.answer(
            f"""
Ваше новое имя пользователя: {msg.text}.
Введите email:
            """,
        )

    async def process_email(
        self,
        msg: types.Message,
        state: FSMContext,
    ) -> types.Message:
        """Process new user email."""

        client_id = msg.from_user.id if msg.from_user else msg.chat.id
        username = (await state.get_data()).get(
            States.AWAITING_USERNAME,
        )
        creation_response = await self.__user_service.create_user_for_client(
            client_id=client_id,
            name=username,
            email=msg.text,
        )
        if not creation_response:
            return await msg.answer(
                "Введен некорректный email. Попробуйте еще раз:",
            )
        await state.finish()
        return await msg.answer(
            "Вы успешно прошли регистрацию! Теперь вам доступен весь функционал.",
        )

    async def on_my_notes_command(
        self,
        msg: types.Message,
        state: FSMContext,
    ) -> types.Message:
        """Process mynotes command."""

        await state.finish()
        client_id = msg.from_user.id if msg.from_user else msg.chat.id
        registered = await self.__user_service.check_if_user_existent_for_client(
            client_id,
        )
        if not registered:
            return await msg.answer(
                """
Перед тем как использовать эту функцию, вам необходимо пройти регистрацию.
                """,
            )
        internal_user_id = await self.__user_service.get_client_id_by_telegram_id(
            client_id,
        )
        notes = await self.__note_service.get_all_notes_for_client(internal_user_id)
        if not notes:
            return await msg.answer("У вас еще нет заметок.")
        composed_report = self.__note_service.compose_report_on_notes(notes)
        return await msg.answer(composed_report)

    async def on_add_note_command(
        self,
        msg: types.Message,
        state: FSMContext,
    ) -> types.Message:
        """Process note creation for client."""

        await state.finish()
        client_id = msg.from_user.id if msg.from_user else msg.chat.id
        registered = await self.__user_service.check_if_user_existent_for_client(
            client_id,
        )
        if not registered:
            return await msg.answer(
                """
Перед тем как использовать эту функцию, вам необходимо пройти регистрацию.
                """,
            )
        await self.__dp.storage.set_state(
            chat=msg.chat.id,
            user=client_id,
            state=States.AWAITING_NOTE_TEXT,
        )
        return await msg.answer(
            "Введите текст для новой заметки:",
        )

    async def process_note_text(
        self,
        msg: types.Message,
        state: FSMContext,
    ) -> types.Message:
        """Process new note text."""

        client_id = msg.from_user.id if msg.from_user else msg.chat.id
        await state.update_data(
            {
                States.AWAITING_NOTE_TEXT: msg.text,
            },
        )
        await self.__dp.storage.set_state(
            chat=msg.chat.id,
            user=client_id,
            state=States.AWAITING_NOTE_REMINDER_TIME,
        )
        return await msg.answer(
            "Введите время напоминания в формате HH:mm:",
        )

    async def process_reminder_time(
        self,
        msg: types.Message,
        state: FSMContext,
    ) -> types.Message:
        """Process new note reminder time."""

        client_id = msg.from_user.id if msg.from_user else msg.chat.id
        text = (await state.get_data()).get(
            States.AWAITING_NOTE_TEXT,
        )
        internal_user_id = await self.__user_service.get_client_id_by_telegram_id(
            client_id,
        )
        creation_response = await self.__note_service.create_note(
            internal_user_id,
            text,
            msg.text,
        )
        if not creation_response:
            return await msg.answer(
                "Некорректный формат времени уведомления. Попробуйте еще раз:",
            )
        await state.finish()
        return await msg.answer("Вы успешно создали новую заметку!")

    def __register_handlers(self):
        """Register all messages handlers."""

        self.__dp.register_message_handler(
            self.on_start_command,
            commands=["start"],
            state="*",
        )
        self.__dp.register_message_handler(
            self.on_my_notes_command,
            commands=["mynotes"],
            state="*",
        )
        self.__dp.register_message_handler(
            self.on_add_note_command,
            commands=["addnote"],
            state="*",
        )
        self.__dp.register_message_handler(
            self.process_username,
            state=States.AWAITING_USERNAME,
        )
        self.__dp.register_message_handler(
            self.process_email,
            state=States.AWAITING_EMAIL,
        )
        self.__dp.register_message_handler(
            self.process_note_text,
            state=States.AWAITING_NOTE_TEXT,
        )
        self.__dp.register_message_handler(
            self.process_reminder_time,
            state=States.AWAITING_NOTE_REMINDER_TIME,
        )

    async def process_update(self, update: types.Update):
        """Process update via dispatcher."""

        Dispatcher.set_current(self.__dp)
        Bot.set_current(self.__telegram_bot_client.get_bot())
        await self.__dp.process_update(update)

    async def set_webhook(self):
        """Sets webhook for bot."""

        webhook_info = await self.__telegram_bot_client.get_bot().get_webhook_info()
        if webhook_info.url != self.__webhook_url:
            await self.__telegram_bot_client.get_bot().set_webhook(self.__webhook_url)

    async def close_session(self):
        """Closes bot session."""

        await self.__telegram_bot_client.get_bot().close()

    def get_dispatcher(self) -> Dispatcher:
        """Get dispatcher from service."""

        return self.__dp

    def get_bot(self) -> Bot:
        """Get bot from service."""

        return self.__telegram_bot_client.get_bot()

"""Telegram service."""


from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from app.pkg.clients import TelegramBotClient
from app.pkg.logger import get_logger


class TelegramService:
    """Contains all handlers for Telegram Bot.

    New clients requests are being processed in it.
    """

    __logger = get_logger(__name__)
    __webhook_url: str
    __telegram_bot_client: TelegramBotClient
    __dp: Dispatcher

    def __init__(
        self,
        telegram_bot_client: TelegramBotClient,
        webhook_url: str,
    ):

        self.__webhook_url = webhook_url
        self.__telegram_bot_client = telegram_bot_client
        self.__dp = Dispatcher(telegram_bot_client.get_bot(), storage=MemoryStorage())

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

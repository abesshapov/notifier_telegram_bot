"""Telegram wallet client."""

import typing
from logging import Logger
from pydantic import SecretStr

from aiogram import Bot, types

from app.pkg.logger import get_logger

_T = typing.TypeVar("_T")


class TelegramBotClient:
    """Telegram bot client."""

    __bot: Bot
    __logger: Logger = get_logger(__name__)

    def __init__(
        self,
        token: SecretStr,
    ):
        self.__bot = Bot(token.get_secret_value())

    def get_bot(self) -> Bot:
        """Get telegram bot instance."""

        return self.__bot

    async def send_message(self, chat_id: int, text: str) -> types.Message:
        """Send message via telegram bot."""

        return await self.__bot.send_message(
            chat_id=chat_id,
            text=text,
        )

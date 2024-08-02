"""User service."""

from typing import Optional

import pydantic
from email_validator import EmailNotValidError, validate_email

from app.internal.repository.postgresql.users import UserRepository
from app.pkg.logger import get_logger
from app.pkg.models.app.users import repository
from app.pkg.models.exceptions.repository import EmptyResult


class UserService:
    """All user-related operations are handled in that service."""

    __logger = get_logger(__name__)
    __user_repository: UserRepository

    def __init__(self, user_repository: UserRepository):

        self.__user_repository = user_repository

    async def check_if_user_existent_for_client(
        self,
        client_id: pydantic.NonNegativeInt,
    ) -> bool:
        """Check if user is already created.

        Returns bool following the request.
        """

        try:
            await self.__user_repository.read(
                repository.ReadUserQueryByTelegramId(
                    telegram_id=client_id,
                ),
            )
            return True
        except EmptyResult:
            return False

    async def create_user_for_client(
        self,
        client_id: pydantic.NonNegativeInt,
        name: str,
        email: str,
    ) -> bool:
        """Creates user for client.

        Before that, checks if email is valid. If not - return False.
        Upon success return True.
        """

        try:
            validate_email(email)
        except EmailNotValidError:
            return False

        await self.__user_repository.create(
            repository.CreateUserCommand(
                telegram_id=client_id,
                email=email,
                name=name,
            ),
        )
        return True

    async def get_client_id_by_telegram_id(
        self,
        client_id: pydantic.NonNegativeInt,
    ) -> Optional[pydantic.NonNegativeInt]:
        """Get client internal id by telegram id."""

        try:
            return (
                await self.__user_repository.read(
                    repository.ReadUserQueryByTelegramId(
                        telegram_id=client_id,
                    ),
                )
            ).id
        except EmptyResult:
            return None

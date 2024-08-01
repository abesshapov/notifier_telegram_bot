"""User model fields."""

from pydantic import Field, NonNegativeInt

from app.pkg.models.base import BaseModel


class BaseUser(BaseModel):
    """Base model for user."""


class UserFields(BaseUser):
    """User fields."""

    class Identifiers(BaseUser):
        """Identitifiers fields."""

        id: NonNegativeInt = Field(
            description="User identifier.",
            example=0,
        )

    class Name(BaseUser):
        """Name fields."""

        name: str = Field(
            description="User name.",
            example="peter",
        )

    class Email(BaseUser):
        """Email fields."""

        email: str = Field(
            description="User email.",
            example="test@gmail.com",
        )

    class TelegramId(BaseUser):
        """Telegram id fields."""

        telegram_id: NonNegativeInt = Field(
            description="User telegram id.",
            example=111,
        )

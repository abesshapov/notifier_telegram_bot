"""Note model fields."""

from datetime import datetime, time

from pydantic import Field, NonNegativeInt

from app.pkg.models.base import BaseModel


class BaseNote(BaseModel):
    """Base model for Note."""


class NoteFields(BaseNote):
    """Note fields."""

    class Identifiers(BaseNote):
        """Identitifiers fields."""

        id: NonNegativeInt = Field(
            description="Note identifier.",
            example=0,
        )

    class UserId(BaseNote):
        """User id fields."""

        user_id: NonNegativeInt = Field(
            description="Note user id.",
            example=111,
        )

    class Text(BaseNote):
        """Text fields."""

        text: str = Field(
            description="Note text.",
            example="Turn off iron",
        )

    class ReminderTime(BaseNote):
        """Reminder time fields."""

        reminder_time: time = Field(
            description="Note reminder time.",
            example=datetime.now().time(),
        )

    class Notified(BaseNote):
        """Notified fields."""

        notified: bool = Field(
            description="Specifies if user was notified on note.",
            example=True,
        )

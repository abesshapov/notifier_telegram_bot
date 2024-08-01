"""Callback model fields."""
import uuid

from pydantic import Field

from app.pkg.models.base import BaseModel


class BaseCallback(BaseModel):
    """Base model for callback."""


class CallbackFields(BaseCallback):
    """Callback fields."""

    class Identifiers(BaseCallback):
        """Identitifiers fields."""

        id: uuid.UUID = Field(
            "Callback identifier.",
            example=uuid.uuid4(),
        )

    class RawBody(BaseCallback):
        """Raw body fields."""

        body: dict = Field(
            "Callback body.",
            example={},
        )

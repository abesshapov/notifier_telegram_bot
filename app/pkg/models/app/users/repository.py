"""User repository models."""

from app.pkg.models.app.users import UserFields
from app.pkg.models.base.model import BaseModel


class CreateUserCommand(UserFields.Name, UserFields.Email, UserFields.TelegramId):
    """Create User command."""


class ReadQuery(BaseModel):
    """Read query base model."""


class ReadUserQueryByTelegramId(ReadQuery, UserFields.TelegramId):
    """Read User query."""


class ReadUserQueryById(ReadQuery, UserFields.Identifiers):
    """Read user query by id."""


class UserResponse(
    UserFields.Identifiers,
    UserFields.Name,
    UserFields.Email,
    UserFields.TelegramId,
):
    """User response."""


class DeleteUserCommand(UserFields.Identifiers):
    """Delete User command."""

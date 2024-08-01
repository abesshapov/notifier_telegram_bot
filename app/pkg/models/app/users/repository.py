"""User repository models."""

from app.pkg.models.app.users import UserFields


class CreateUserCommand(UserFields.Name, UserFields.Email, UserFields.TelegramId):
    """Create User command."""


class ReadUserQuery(UserFields.TelegramId):
    """Read User query."""


class UserResponse(
    UserFields.Identifiers,
    UserFields.Name,
    UserFields.Email,
    UserFields.TelegramId,
):
    """User response."""


class DeleteUserCommand(UserFields.Identifiers):
    """Delete User command."""

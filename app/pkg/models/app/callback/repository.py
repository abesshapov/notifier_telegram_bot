"""Callback repository models."""
from app.pkg.models.app.callback import CallbackFields


class CreateCallbackCommand(CallbackFields.RawBody):
    """Create callback command."""


class ReadCallbackQuery(CallbackFields.Identifiers):
    """Read callback query."""


class CallbackResponse(CallbackFields.Identifiers, CallbackFields.RawBody):
    """Callback response."""


class UpdateCallbackCommand(CallbackFields.Identifiers, CallbackFields.RawBody):
    """Update callback command."""


class DeleteCallbackCommand(CallbackFields.Identifiers):
    """Delete callback command."""

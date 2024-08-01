"""Callback models received from the client."""

from app.pkg.models.app.callback import CallbackFields


class ReadCallbackQuery(CallbackFields.Identifiers):
    """Read callback query."""


class CallbackAPIResponse(CallbackFields.Identifiers, CallbackFields.RawBody):
    """Callback API response."""

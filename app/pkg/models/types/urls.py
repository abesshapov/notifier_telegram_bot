"""Https urls for the app."""

from pydantic import AnyUrl


class HttpsUrl(AnyUrl):
    """Https url type."""

    allowed_schemes = {"https"}
    tld_required = True
    max_length = 2000

    __slots__ = {}

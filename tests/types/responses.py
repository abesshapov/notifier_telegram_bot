"""Classes for type checking in `router.responses` module."""
from __future__ import annotations

import typing

import httpx

from app.pkg.models.base import BaseAPIException, Model


class ResponseWithErrorType(typing.Protocol):
    def __call__(
        self,
        response: httpx.Response,
        expected_error: type[BaseAPIException],
        relative_occurrence: bool | None = False,
    ) -> bool:
        """Protocol of calling function in
        `router.responses:response_without_error`"""


class ResponseEqual(typing.Protocol):
    def __call__(
        self,
        response: httpx.Response,
        expected_model: list[Model] | Model,
        expected_status_code: int,
        ignore: list[type[Model]] | None = None,
    ):
        """Protocol of calling function in `router.responses:response_equal`"""

"""Module for type hints of the equals method of the models."""

import typing

from app.pkg.models.base import Model

C = typing.TypeVar("C", bound=typing.Callable)  # placeholder for any Callable


class CheckArrayEqualityType(typing.Protocol[C]):
    actual: typing.List[typing.Any]
    expected: typing.List[typing.Any]

    __call__: bool


class CheckModelsEqualityType(typing.Protocol[C]):
    actual: Model
    expected: Model
    ignore: typing.Optional[typing.List[str]]

    __call__: bool

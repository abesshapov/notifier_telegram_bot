"""Type definitions for inserters."""

import typing

C = typing.TypeVar("C", bound=typing.Callable)  # placeholder for any Callable


class InserterType(typing.Protocol[C]):
    __call__: C

"""Type definitions for generators."""

import typing

C = typing.TypeVar("C", bound=typing.Callable)  # placeholder for any Callable


class GeneratorType(typing.Protocol[C]):
    __call__: C

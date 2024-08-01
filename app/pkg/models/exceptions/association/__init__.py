"""Association driver error with python exceptions."""

from psycopg2 import errorcodes

from app.pkg.models.exceptions import repository

__aiopg__ = {
    errorcodes.UNIQUE_VIOLATION: repository.UniqueViolation,
}

# TODO: Make this dict more flexible.
#       Like `Container` class in `/app/pkg/models/core/container.py`
#       Add support for owerwrite exceptions in `__aiopg__` dict.
__constrains__ = {}

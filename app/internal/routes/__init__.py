"""Global point for collected routers. __routes__ is a :class:`.Routes`
instance that contains all routers in your application.

Examples:
    After declaring all routers, you need to register them in your application::

        >>> from fastapi import FastAPI
        >>> app = FastAPI()
        >>> __routes__.register_routes(app=app)
"""
from fastapi import APIRouter

from app.pkg.models.base import BaseEnum
from app.pkg.models.core.routes import Routes


class Tags(BaseEnum):
    WEBHOOKS = "webhooks"


__routes__ = Routes(
    routers=(),
)

"""``on_startup`` function will be called when server trying to start."""
from contextlib import asynccontextmanager

from dependency_injector.wiring import inject
from fastapi import FastAPI


@asynccontextmanager
@inject
async def lifespan(
    app: FastAPI,  # pylint: disable=unused-argument # noqa: F841
) -> None:  # type: ignore
    """Run code on server startup.

    Warnings:
        **Don't use this function for insert default data in database.
        For this action, we have scripts/migrate.py.**

    Returns:
        None
    """
    yield

"""``on_startup`` function will be called when server trying to start."""
from contextlib import asynccontextmanager

from dependency_injector.wiring import Provide, inject
from fastapi import FastAPI

from app.internal.services import Services
from app.internal.services.telegram import TelegramService


@asynccontextmanager
@inject
async def lifespan(
    app: FastAPI,  # pylint: disable=unused-argument # noqa: F841
    telegram_service: TelegramService = Provide[Services.telegram_service],
) -> None:  # type: ignore
    """Run code on server startup.

    Warnings:
        **Don't use this function for insert default data in database.
        For this action, we have scripts/migrate.py.**

    Returns:
        None
    """

    await telegram_service.set_webhook()
    yield
    await telegram_service.close_session()

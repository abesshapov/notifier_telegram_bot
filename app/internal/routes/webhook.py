"""Webhooks router for telegram bot requests processing."""

from aiogram import types
from dependency_injector.wiring import Provide, inject
from fastapi import Depends, status

from app.internal.routes import webhooks_router
from app.internal.services import Services, TelegramService
from app.pkg.settings import settings


@webhooks_router.post(
    f"{settings.TELEGRAM.WEBHOOK_PATH}",
    summary="Handles telegram requests",
    description="",
    response_model=None,
    status_code=status.HTTP_200_OK,
)
@inject
async def handle_telegram_request(
    update: dict,
    telegram_service: TelegramService = Depends(Provide[Services.telegram_service]),
):
    telegram_update = types.Update(**update)
    await telegram_service.process_update(telegram_update)

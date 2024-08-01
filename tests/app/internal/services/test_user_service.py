"""Tests on user service."""

import pytest

from app.internal.repository.postgresql.users import UserRepository
from app.internal.services.user import UserService
from app.pkg.models.app.users import repository
from app.pkg.models.exceptions.repository import EmptyResult


@pytest.mark.parametrize("existent", [True, False])
async def test_check_if_user_is_existent(
    user_service: UserService,
    user_repository: UserRepository,
    client_id: int,
    existent: bool,
):
    """Test on check if user is existent operation."""

    if existent:
        await user_repository.create(
            repository.CreateUserCommand(
                telegram_id=client_id,
                email="test@mail.ru",
                name="Peter",
            ),
        )
    assert existent == await user_service.check_if_user_existent_for_client(client_id)


@pytest.mark.parametrize("existent", [True, False])
async def test_get_user_internal_id(
    user_service: UserService,
    user_repository: UserRepository,
    client_id: int,
    existent: bool,
):
    """Test on getting user internal id operation."""

    internal_id = None
    if existent:
        internal_id = (
            await user_repository.create(
                repository.CreateUserCommand(
                    telegram_id=client_id,
                    email="test@mail.ru",
                    name="Peter",
                ),
            )
        ).id
    assert internal_id == await user_service.get_client_id_by_telegram_id(client_id)


@pytest.mark.parametrize("email_valid", [True, False])
async def test_user_creation(
    user_service: UserService,
    user_repository: UserRepository,
    client_id: int,
    email_valid: bool,
):
    """Test on user creation."""

    email = "test@mail.ru" if email_valid else "invalid 100%"
    response = await user_service.create_user_for_client(
        client_id=client_id,
        name="Peter",
        email=email,
    )
    assert email_valid == response

    if email_valid:
        user = await user_repository.read(
            repository.ReadUserQueryByTelegramId(telegram_id=client_id),
        )
        assert user.email == email
        assert user.name == "Peter"

    else:
        with pytest.raises(EmptyResult):
            await user_repository.read(
                repository.ReadUserQueryByTelegramId(telegram_id=client_id),
            )

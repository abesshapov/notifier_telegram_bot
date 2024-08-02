"""Test on user repository."""

import pytest

from app.internal.repository.postgresql.users import UserRepository
from app.pkg.models.app.users import repository
from app.pkg.models.exceptions.repository import EmptyResult


async def test_on_user_creation(
    user_repository: UserRepository,
    client_id: int,
):
    """Test on user creation via repository."""

    creation_response = await user_repository.create(
        repository.CreateUserCommand(
            telegram_id=client_id,
            email="some@email",
            name="Alex",
        ),
    )

    assert creation_response.telegram_id == client_id
    assert creation_response.email == "some@email"
    assert creation_response.name == "Alex"


async def test_on_multiple_users_creation(
    user_repository: UserRepository,
    client_id: int,
):
    """Test on multiple users creation."""

    creation_response = await user_repository.create(
        repository.CreateUserCommand(
            telegram_id=client_id,
            email="some@email",
            name="Alex",
        ),
    )

    another_creation_response = await user_repository.create(
        repository.CreateUserCommand(
            telegram_id=client_id,
            email="some@email",
            name="Alex",
        ),
    )
    assert another_creation_response.to_dict() == creation_response.to_dict() | {
        "id": creation_response.id + 1,
    }, "Id of the user should be more than previous ones by one."


@pytest.mark.parametrize("read_by", ["id", "telegram_id"])
async def test_on_specific_user_reading(
    user_repository: UserRepository,
    client_id: int,
    read_by: str,
):
    """Test on specifi user reading."""

    creation_response = await user_repository.create(
        repository.CreateUserCommand(
            telegram_id=client_id,
            email="some@email",
            name="Alex",
        ),
    )

    if read_by == "id":
        query = repository.ReadUserQueryById(
            id=creation_response.id,
        )
    if read_by == "telegram_id":
        query = repository.ReadUserQueryByTelegramId(
            telegram_id=creation_response.telegram_id,
        )

    read_response = await user_repository.read(
        query,
    )
    assert read_response == creation_response


async def test_on_all_users_reading(
    user_repository: UserRepository,
    client_id: int,
):
    """Test on all users reading."""

    try:
        initial_users = await user_repository.read_all()
    except EmptyResult:
        initial_users = []

    creation_response = await user_repository.create(
        repository.CreateUserCommand(
            telegram_id=client_id,
            email="some@email",
            name="Alex",
        ),
    )

    eventual_users = await user_repository.read_all()
    assert creation_response in eventual_users
    assert len(eventual_users) == len(initial_users) + 1


async def test_on_user_deletion(
    user_repository: UserRepository,
    client_id: int,
):
    """Test on user deletion."""

    creation_response = await user_repository.create(
        repository.CreateUserCommand(
            telegram_id=client_id,
            email="some@email",
            name="Alex",
        ),
    )

    deletion_response = await user_repository.delete(
        repository.DeleteUserCommand(
            id=creation_response.id,
        ),
    )
    assert creation_response == deletion_response

    with pytest.raises(EmptyResult):
        await user_repository.read(
            repository.ReadUserQueryById(
                id=creation_response.id,
            ),
        )

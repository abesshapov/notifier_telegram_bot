"""User information repository."""

from typing import List

from app.internal.repository.postgresql.connection import get_connection
from app.internal.repository.postgresql.handlers.collect_response import (
    collect_response,
)
from app.internal.repository.repository import Repository
from app.pkg.models.app.users import repository


class UserRepository(Repository):
    """User repository."""

    @collect_response
    async def create(
        self,
        cmd: repository.CreateUserCommand,
    ) -> repository.UserResponse:
        """Create User."""
        q = """
            insert into users (
                name,
                email,
                telegram_id
            )
            values (
                %(name)s,
                %(email)s,
                %(telegram_id)s
            )
            returning
                id,
                name,
                email,
                telegram_id;
        """
        async with get_connection() as cur:
            await cur.execute(q, cmd.to_dict(show_secrets=True, is_json=True))
            return await cur.fetchone()

    @collect_response
    async def read(
        self,
        query: repository.ReadQuery,
    ) -> repository.UserResponse:
        """Read User."""
        q = self.__create_read_query(query)
        async with get_connection() as cur:
            await cur.execute(q, query.to_dict())
            return await cur.fetchone()

    @collect_response
    async def delete(
        self,
        cmd: repository.DeleteUserCommand,
    ) -> repository.UserResponse:
        """Delete User."""
        q = """
            delete from users
            where id = %(id)s
            returning
                id,
                name,
                email,
                telegram_id;
        """
        async with get_connection() as cur:
            await cur.execute(q, cmd.to_dict())
            return await cur.fetchone()

    @collect_response
    async def read_all(self) -> List[repository.UserResponse]:
        """Read all Users."""
        q = """
            select
                id,
                name,
                email,
                telegram_id
            from users
            order by id desc;
        """
        async with get_connection() as cur:
            await cur.execute(q)
            return await cur.fetchall()

    def __create_read_query(
        self,
        query: repository.ReadQuery,
    ) -> str:
        """Compose read query."""

        if isinstance(query, repository.ReadUserQueryById):
            q = """
                select
                    id,
                    name,
                    email,
                    telegram_id
                from users
                where id = %(id)s;
            """

        if isinstance(query, repository.ReadUserQueryByTelegramId):
            q = """
                select
                    id,
                    name,
                    email,
                    telegram_id
                from users
                where telegram_id = %(telegram_id)s;
            """
        return q

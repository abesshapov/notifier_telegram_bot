"""Note information repository."""

from typing import List

from app.internal.repository.postgresql.connection import get_connection
from app.internal.repository.postgresql.handlers.collect_response import (
    collect_response,
)
from app.internal.repository.repository import Repository
from app.pkg.models.app.notes import repository


class NoteRepository(Repository):
    """Note repository."""

    @collect_response
    async def create(
        self,
        cmd: repository.CreateNoteCommand,
    ) -> repository.NoteResponse:
        """Create Note."""
        q = """
            insert into notes (
                user_id,
                text,
                reminder_time
            )
            values (
                %(user_id)s,
                %(text)s,
                %(reminder_time)s
            )
            returning
                id,
                user_id,
                text,
                reminder_time,
                notified;
        """
        async with get_connection() as cur:
            await cur.execute(q, cmd.to_dict(show_secrets=True, is_json=True))
            return await cur.fetchone()

    @collect_response
    async def read(
        self,
        query: repository.ReadNoteQueryById,
    ) -> repository.NoteResponse:
        """Read Note."""
        q = """
            select
                id,
                user_id,
                text,
                reminder_time,
                notified
            from notes
            where id = %(id)s;
        """
        async with get_connection() as cur:
            await cur.execute(q, query.to_dict())
            return await cur.fetchone()

    @collect_response
    async def read_for_user(
        self,
        query: repository.ReadNotesQueryByUserId,
    ) -> List[repository.NoteResponse]:
        """Read notes for user."""
        q = """
            select
                id,
                user_id,
                text,
                reminder_time,
                notified
            from notes
            where user_id = %(user_id)s;
        """
        async with get_connection() as cur:
            await cur.execute(q, query.to_dict())
            return await cur.fetchall()

    @collect_response
    async def read_all(self) -> List[repository.NoteResponse]:
        """Read all Notes."""
        q = """
            select
                id,
                user_id,
                text,
                reminder_time,
                notified
            from notes
            order by id desc;
        """
        async with get_connection() as cur:
            await cur.execute(q)
            return await cur.fetchall()

    @collect_response
    async def update(
        self,
        cmd: repository.UpdateNoteNotifiedStateCommand,
    ) -> repository.NoteResponse:
        """Update note notified state."""

        q = """
            update notes
                set notified = %(notified)s
                where id = %(id)s
            returning
                id,
                user_id,
                text,
                reminder_time,
                notified;
        """
        async with get_connection() as cur:
            await cur.execute(q, cmd.to_dict())
            return await cur.fetchone()

    @collect_response
    async def delete(
        self,
        cmd: repository.DeleteNoteCommand,
    ) -> repository.NoteResponse:
        """Delete Note."""
        q = """
            delete from notes
            where id = %(id)s
            returning
                id,
                user_id,
                text,
                reminder_time,
                notified;
        """
        async with get_connection() as cur:
            await cur.execute(q, cmd.to_dict())
            return await cur.fetchone()

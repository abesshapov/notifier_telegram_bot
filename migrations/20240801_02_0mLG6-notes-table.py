"""
notes-table
"""

from yoyo import step

__depends__ = {'20240801_01_3kbap-added-users-table'}

steps = [
    step(
        """
        CREATE TABLE if not exists notes (
            id serial primary key,
            user_id integer references users(id),
            text text,
            reminder_time timestamp,
            notified boolean default FALSE
        );
        """,
        "drop table if exists notes;"
    )
]

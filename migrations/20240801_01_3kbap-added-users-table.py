"""
added users table
"""

from yoyo import step

__depends__ = {}

steps = [
    step(
        """
        CREATE TABLE if not exists users (
            id serial primary key,
            name text,
            email text,
            telegram_id bigint
        );
        """,
        "drop table if exists users cascade;"
    )

]

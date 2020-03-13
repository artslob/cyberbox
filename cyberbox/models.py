from uuid import uuid4

import sqlalchemy
from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import expression

metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("uid", UUID(), default=uuid4, primary_key=True),
    sqlalchemy.Column("username", String(), nullable=False, unique=True),
    sqlalchemy.Column(
        "disabled", Boolean(), nullable=False, default=False, server_default=expression.false()
    ),
    sqlalchemy.Column("hashed_password", String(), nullable=False),
)

files = sqlalchemy.Table(
    "files",
    metadata,
    sqlalchemy.Column("uid", UUID(), primary_key=True),
    sqlalchemy.Column("owner", String(), ForeignKey(users.c.username), nullable=False),
    sqlalchemy.Column("filename", String(), nullable=False),
    sqlalchemy.Column("content_type", String(), nullable=False),
)

links = sqlalchemy.Table(
    "links",
    metadata,
    sqlalchemy.Column("uid", UUID(), ForeignKey(files.c.uid)),
    sqlalchemy.Column("link", String(), unique=True, nullable=False),
    sqlalchemy.Column(
        "is_onetime", Boolean(), default=False, server_default=expression.false(), nullable=False
    ),
    # TODO created time
    sqlalchemy.Column("visited_count", Integer(), default=0, server_default="0", nullable=False),
)

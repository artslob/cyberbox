from uuid import uuid4

import sqlalchemy
from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import expression

metadata = sqlalchemy.MetaData()

User = sqlalchemy.Table(
    "user",
    metadata,
    Column("uid", UUID(), default=uuid4, primary_key=True),
    Column("username", String(), nullable=False, unique=True),
    Column("disabled", Boolean(), nullable=False, default=False, server_default=expression.false()),
    Column("hashed_password", String(), nullable=False),
)

File = sqlalchemy.Table(
    "file",
    metadata,
    Column("uid", UUID(), primary_key=True),
    Column("owner", String(), ForeignKey(User.c.username), nullable=False),
    Column("filename", String(), nullable=False),
    Column("content_type", String(), nullable=False),
    Column("created", TIMESTAMP(timezone=True), nullable=False),
)

Link = sqlalchemy.Table(
    "link",
    metadata,
    Column("uid", UUID(), ForeignKey(File.c.uid)),
    Column("link", String(), unique=True, nullable=False),
    Column(
        "is_onetime", Boolean(), default=False, server_default=expression.false(), nullable=False
    ),
    Column("created", TIMESTAMP(timezone=True), nullable=False),
    Column("visited_count", Integer(), default=0, server_default="0", nullable=False),
    Column("valid_until", TIMESTAMP(timezone=True), nullable=True),
)

# TODO set on_delete on_update

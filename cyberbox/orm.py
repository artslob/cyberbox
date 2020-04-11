from uuid import uuid4

import sqlalchemy
from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import expression

naming_convention = {
    "ix": "ix_%(column_0_N_label)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s_%(referred_column_0_N_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = sqlalchemy.MetaData(naming_convention=naming_convention)

CASCADE = "CASCADE"

User = sqlalchemy.Table(
    "user",
    metadata,
    Column("uid", UUID(), default=uuid4, primary_key=True),
    Column("username", String(), nullable=False, unique=True),
    Column("disabled", Boolean(), nullable=False, default=False, server_default=expression.false()),
    Column("hashed_password", String(), nullable=False),
    Column("is_admin", Boolean(), server_default=expression.false(), nullable=False),
    Column("created", TIMESTAMP(timezone=True), nullable=False, index=True),
)

File = sqlalchemy.Table(
    "file",
    metadata,
    Column("uid", UUID(), primary_key=True),
    Column(
        "owner",
        String(),
        ForeignKey(User.c.username, onupdate=CASCADE, ondelete=CASCADE),
        nullable=False,
        index=True,
    ),
    Column("filename", String(), nullable=False),
    Column("content_type", String(), nullable=False),
    Column("created", TIMESTAMP(timezone=True), nullable=False, index=True),
)

Link = sqlalchemy.Table(
    "link",
    metadata,
    Column(
        "uid",
        UUID(),
        ForeignKey(File.c.uid, onupdate=CASCADE, ondelete=CASCADE),
        nullable=False,
        index=True,
    ),
    Column("link", String(), primary_key=True),
    Column(
        "is_onetime", Boolean(), default=False, server_default=expression.false(), nullable=False
    ),
    Column("created", TIMESTAMP(timezone=True), nullable=False, index=True),
    Column("visited_count", Integer(), default=0, server_default="0", nullable=False),
    Column("valid_until", TIMESTAMP(timezone=True), nullable=True),
)

from uuid import uuid4

import sqlalchemy
from sqlalchemy import Boolean, String
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

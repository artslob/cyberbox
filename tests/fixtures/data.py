from uuid import uuid4

import pytest
from databases import Database

from cyberbox.models import users
from cyberbox.routes.auth import crypt_context


@pytest.fixture()
async def create_users(db: Database):
    hashed_password = crypt_context.hash("123")
    await db.execute_many(
        users.insert(),
        [
            dict(uid=uuid4(), username=username, disabled=disabled, hashed_password=hashed_password)
            for username, disabled in [
                ("test_user", False),
                ("disabled_user", True),
                ("active_user", False),
            ]
        ],
    )

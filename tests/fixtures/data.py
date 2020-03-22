from pathlib import Path
from uuid import uuid4

import pytest
from databases import Database
from httpx import AsyncClient

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


@pytest.fixture()
async def create_files(logged_user, active_user, client: AsyncClient, tmp_path: Path):
    for user_data in logged_user, active_user:
        for _ in range(40):
            username, access_token, headers = user_data

            uid = str(uuid4())
            test_file = tmp_path / uid
            test_file.write_text(uid)

            with test_file.open() as f:
                response = await client.post("/files/upload", files=dict(file=f), headers=headers)

            assert response.status_code == 200

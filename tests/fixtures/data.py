from pathlib import Path
from uuid import uuid4

import pytest
from httpx import AsyncClient


@pytest.fixture()
async def create_files(logged_user, active_user, client: AsyncClient, tmp_path: Path):
    for user_data in logged_user, active_user:
        for _ in range(40):
            username, access_token, headers = user_data

            uid = str(uuid4())
            test_file = tmp_path / uid
            test_file.write_text(uid)

            with test_file.open() as f:
                response = await client.post("/file/upload", files=dict(file=f), headers=headers)

            assert response.status_code == 200

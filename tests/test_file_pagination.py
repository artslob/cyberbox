from uuid import uuid4

import arrow
import pytest
from databases import Database
from httpx import AsyncClient
from sqlalchemy import func, select
from starlette import status

from cyberbox import orm


@pytest.fixture()
async def create_data_for_test(db: Database, logged_user):
    username, access_token, headers = logged_user

    async def create(count: int):
        values = [
            dict(
                uid=uuid4(),
                owner=username,
                filename=f"f{i}",
                content_type="",
                created=arrow.utcnow().datetime,
            )
            for i in range(count)
        ]
        await db.execute_many(orm.File.insert(), values)

    return create


@pytest.mark.asyncio
async def test_file_pagination(
    create_data_for_test, db: Database, client: AsyncClient, logged_user
):
    username, access_token, headers = logged_user

    await create_data_for_test(12)
    assert await db.execute(select([func.count()]).select_from(orm.File)) == 12

    response = await client.get("/file", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert len(json["items"]) == 12
    assert [i["filename"] for i in json["items"]] == [f"f{i}" for i in range(12)]
    assert json["total"] == 12
    assert json["pages"] == 1
    assert json["has_next"] is False
    assert json["has_previous"] is False
    assert json["next_page_number"] is None
    assert json["previous_page_number"] is None

from uuid import uuid4

import arrow
import pytest
from databases import Database
from httpx import AsyncClient
from sqlalchemy import func, select
from starlette import status

from cyberbox import orm

active_file_uid = uuid4()


@pytest.fixture()
async def data_for_test(logged_user, active_user, db: Database):
    username, access_token, headers = logged_user

    file_uid = uuid4()

    await db.execute(
        orm.File.insert(),
        dict(
            uid=file_uid,
            owner=username,
            filename="logged_file",
            content_type="",
            created=arrow.utcnow().datetime,
        ),
    )

    await db.execute_many(
        orm.Link.insert(),
        [
            dict(
                uid=file_uid,
                link=str(i),
                is_onetime=False,
                created=arrow.utcnow().datetime,
                visited_count=0,
            )
            for i in range(2)
        ],
    )

    # same for active user

    username, access_token, headers = active_user

    await db.execute(
        orm.File.insert(),
        dict(
            uid=active_file_uid,
            owner=username,
            filename="active_file",
            content_type="",
            created=arrow.utcnow().datetime,
        ),
    )

    await db.execute_many(
        orm.Link.insert(),
        [
            dict(
                uid=active_file_uid,
                link=str(i),
                is_onetime=False,
                created=arrow.utcnow().datetime,
                visited_count=0,
            )
            for i in range(2, 4)
        ],
    )

    assert await db.execute(select([func.count()]).select_from(orm.File)) == 2
    assert await db.execute(select([func.count()]).select_from(orm.Link)) == 4


@pytest.mark.asyncio
async def test_link_pagination(data_for_test, active_user, client: AsyncClient):
    username, access_token, headers = active_user
    response = await client.get("/link", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert [i["link"] for i in response.json()["items"]] == ["2", "3"]

    response = await client.get("/link", headers=headers, params=dict(file_uid=str(uuid4())))
    assert response.status_code == status.HTTP_200_OK
    assert [i["link"] for i in response.json()["items"]] == []

    response = await client.get(
        "/link", headers=headers, params=dict(file_uid=str(active_file_uid))
    )
    assert response.status_code == status.HTTP_200_OK
    assert [i["link"] for i in response.json()["items"]] == ["2", "3"]

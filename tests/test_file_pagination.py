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
@pytest.mark.parametrize(
    "count, page, limit, items_len, expected_items, total, pages, has_next, has_previous, "
    "next_page_number, previous_page_number",
    [
        [12, None, None, 12, [f"f{i}" for i in range(12)], 12, 1, False, False, None, None],
        [12, 1, 5, 5, [f"f{i}" for i in range(5)], 12, 3, True, False, 2, None],
        [12, 2, 5, 5, [f"f{i}" for i in range(5, 10)], 12, 3, True, True, 3, 1],
        [12, 3, 5, 2, [f"f{i}" for i in range(10, 12)], 12, 3, False, True, None, 2],
        [12, 4, 5, 0, [], 12, 3, False, True, None, 3],
        [12, 5, 5, 0, [], 12, 3, False, True, None, 4],
        [10, 2, 5, 5, [f"f{i}" for i in range(5, 10)], 10, 2, False, True, None, 1],
    ],
)
async def test_file_pagination(
    create_data_for_test,
    db: Database,
    client: AsyncClient,
    logged_user,
    count,
    page,
    limit,
    items_len,
    expected_items,
    total,
    pages,
    has_next,
    has_previous,
    next_page_number,
    previous_page_number,
):
    username, access_token, headers = logged_user

    await create_data_for_test(count)
    assert await db.execute(select([func.count()]).select_from(orm.File)) == count

    response = await client.get("/file", headers=headers, params=dict(_page=page, _limit=limit))
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert len(json["items"]) == items_len
    assert [i["filename"] for i in json["items"]] == expected_items
    assert json["total"] == total
    assert json["pages"] == pages
    assert json["has_next"] == has_next
    assert json["has_previous"] == has_previous
    assert json["next_page_number"] == next_page_number
    assert json["previous_page_number"] == previous_page_number

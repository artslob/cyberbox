from pathlib import Path

import arrow
import pytest
from databases import Database
from httpx import AsyncClient
from sqlalchemy import func, select

from cyberbox.models import links
from cyberbox.routes.links import Link


@pytest.mark.asyncio
async def test_create_link_by_not_owner(active_user, upload_file: dict, client: AsyncClient):
    """ Check that not owner cannot create link for some file. """
    username, access_token, headers = active_user

    file_uid = upload_file["uid"]
    response = await client.post(f"/links/{file_uid}", json=dict(is_onetime=False), headers=headers)
    assert response.status_code == 404
    assert response.json() == {"detail": f"File with uuid '{file_uid}' not found"}


@pytest.fixture()
async def create_link_factory(logged_user, upload_file: dict, client: AsyncClient):
    async def _create_link(params: dict):
        username, access_token, headers = logged_user

        file_uid = upload_file["uid"]
        response = await client.post(f"/links/{file_uid}", json=params, headers=headers)
        assert response.status_code == 200
        return response.json()

    return _create_link


@pytest.fixture()
async def create_link(create_link_factory):
    return await create_link_factory(dict(is_onetime=False))


def check_link_info(link_info: dict, upload_file: dict):
    assert link_info["uid"] == upload_file["uid"]
    assert isinstance(link_info["link"], str)
    assert len(link_info["link"]) == 22
    assert link_info["is_onetime"] is False
    assert link_info["visited_count"] == 0
    assert link_info["valid_until"] is None
    assert isinstance(link_info["created"], str)
    assert arrow.get(link_info["created"]) > arrow.utcnow().shift(minutes=-1)


@pytest.mark.asyncio
async def test_link_creation(create_link: dict, upload_file: dict, db: Database):
    assert await db.execute(select([func.count()]).select_from(links)) == 1
    check_link_info(create_link, upload_file)


@pytest.mark.asyncio
async def test_link_info(create_link: dict, client: AsyncClient, upload_file: dict):
    response = await client.get(f"/links/{create_link['link']}/info")
    assert response.status_code == 200

    json = response.json()
    check_link_info(json, upload_file)


@pytest.mark.asyncio
async def test_download_file_by_link(
    create_link: dict, client: AsyncClient, test_file: Path, db: Database
):
    """ Check file can be downloaded by link. Check visited_count was incremented. """
    i, n = 0, 3
    link = create_link["link"]
    for i in range(n):
        response = await client.get(f"/links/{link}")
        assert response.status_code == 200

    assert response.text == test_file.read_text()
    assert response.headers["content-disposition"] == f'attachment; filename="test-file.txt"'

    query = select([links.c.visited_count]).where(links.c.link == link)
    assert await db.execute(query) == n


@pytest.mark.parametrize("minutes_shift, expected_status", [[-10, 404], [10, 200]])
@pytest.mark.asyncio
async def test_valid_until(
    create_link_factory: dict, client: AsyncClient, db: Database, minutes_shift, expected_status
):
    """ Check that when valid_until is in past file cannot be downloaded. """
    valid_until = arrow.utcnow().shift(minutes=minutes_shift).isoformat()
    link_json: dict = await create_link_factory(dict(is_onetime=True, valid_until=valid_until))
    link = link_json["link"]
    assert isinstance(link, str)

    assert link_json["valid_until"] == valid_until

    link_obj = Link.parse_obj(await db.fetch_one(links.select().where(links.c.link == link)))
    assert arrow.get(link_obj.valid_until).isoformat() == valid_until

    response = await client.get(f"/links/{link}")
    assert response.status_code == expected_status


@pytest.mark.asyncio
async def test_download_by_not_existing_link(create_link: dict, client: AsyncClient):
    response = await client.get(f"/links/not-existing-link")
    assert response.status_code == 404
    assert response.json() == {"detail": "Link does not exist"}


@pytest.mark.asyncio
async def test_delete_link(create_link: dict, client: AsyncClient, logged_user, db: Database):
    username, access_token, headers = logged_user

    assert await db.execute(select([func.count()]).select_from(links)) == 1

    response = await client.delete(f"/links/{create_link['link']}", headers=headers)
    assert response.status_code == 200

    assert await db.execute(select([func.count()]).select_from(links)) == 0


@pytest.mark.asyncio
async def test_delete_link_not_owner(create_link: dict, client: AsyncClient, active_user):
    """ Check that not owner cannot delete link of another user. """

    username, access_token, headers = active_user

    link = create_link["link"]
    response = await client.delete(f"/links/{link}", headers=headers)
    assert response.status_code == 404
    assert response.json() == {"detail": f"Link '{link}' does not exist"}

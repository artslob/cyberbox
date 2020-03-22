from pathlib import Path

import pytest
from databases import Database
from httpx import AsyncClient
from sqlalchemy import func, select

from cyberbox.models import links


@pytest.mark.asyncio
async def test_create_link_by_not_owner(active_user, upload_file: dict, client: AsyncClient):
    """ Check that not owner cannot create link for some file. """
    username, access_token, headers = active_user

    file_uid = upload_file["uid"]
    response = await client.post(f"/links/{file_uid}", json=dict(is_onetime=False), headers=headers)
    assert response.status_code == 404
    assert response.json() == {"detail": f"File with uuid '{file_uid}' not found"}


@pytest.fixture()
async def create_link(logged_user, upload_file: dict, client: AsyncClient):
    username, access_token, headers = logged_user

    file_uid = upload_file["uid"]
    response = await client.post(f"/links/{file_uid}", json=dict(is_onetime=False), headers=headers)
    assert response.status_code == 200
    return response.json()


@pytest.mark.asyncio
async def test_link_creation(create_link: dict, upload_file: dict, db: Database):
    assert await db.execute(select([func.count()]).select_from(links)) == 1

    assert create_link["uid"] == upload_file["uid"]
    assert isinstance(create_link["link"], str)
    assert len(create_link["link"]) == 22
    assert create_link["is_onetime"] is False
    assert create_link["visited_count"] == 0


@pytest.mark.asyncio
async def test_link_info(create_link: dict, client: AsyncClient, upload_file: dict):
    response = await client.get(f"/links/{create_link['link']}/info")
    assert response.status_code == 200

    json = response.json()
    assert json["uid"] == upload_file["uid"]
    assert isinstance(json["link"], str)
    assert len(json["link"]) == 22
    assert json["is_onetime"] is False
    assert json["visited_count"] == 0


@pytest.mark.asyncio
async def test_download_file_by_link(create_link: dict, client: AsyncClient, test_file: Path):
    response = await client.get(f"/links/{create_link['link']}")
    assert response.status_code == 200

    assert response.text == test_file.read_text()
    assert response.headers["content-disposition"] == f'attachment; filename="test-file.txt"'


@pytest.mark.asyncio
async def test_download_file_by_link_404(create_link: dict, client: AsyncClient, test_file: Path):
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

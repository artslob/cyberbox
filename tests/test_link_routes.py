import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_link_creation(logged_user, upload_file: dict, client: AsyncClient):
    username, access_token, headers = logged_user

    file_uid = upload_file["uid"]
    response = await client.post(f"/links/{file_uid}", json=dict(is_onetime=False), headers=headers)
    assert response.status_code == 200
    json = response.json()

    assert json["uid"] == file_uid
    assert isinstance(json["link"], str)
    assert len(json["link"]) == 22
    assert json["is_onetime"] is False
    assert json["visited_count"] == 0

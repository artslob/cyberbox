import pytest

content = "some\ncontent"


@pytest.fixture()
def test_file(tmp_path):
    file = tmp_path / "test-file.txt"
    file.write_text(content)
    return file


@pytest.fixture()
async def upload_file(logged_user, client, test_file):
    username, access_token, headers = logged_user

    with test_file.open() as f:
        response = await client.post("/files/upload", files=dict(file=f), headers=headers)

    assert response.status_code == 200
    return response.json()

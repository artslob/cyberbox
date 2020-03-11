from pathlib import Path
from typing import Callable
from uuid import UUID

import pytest
from httpx import AsyncClient

content = "some\ncontent"


@pytest.fixture()
def test_file(tmp_path):
    file = tmp_path / "test-file.txt"
    file.write_text(content)
    return file


def simple_files(file, path):
    return dict(file=file)


def with_content_type(file, path):
    return dict(file=(path.name, file, "text/plain"))


def with_another_name(file, path):
    return dict(file=("another.name.tar.gz", file))


def with_content_type_and_another_name(file, path):
    return dict(file=("another.name.tar.gz", file, "text/plain"))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "files_factory, expected_name, expected_content_type",
    [
        [simple_files, "test-file.txt", "text/plain"],
        [with_content_type, "test-file.txt", "text/plain"],
        [with_another_name, "another.name.tar.gz", "application/x-tar"],
        [with_content_type_and_another_name, "another.name.tar.gz", "text/plain"],
    ],
)
async def test_file_upload_with_file_factory(
    client: AsyncClient,
    test_file: Path,
    logged_user,
    files_factory: Callable,
    expected_name: str,
    expected_content_type: str,
    files_dir: Path,
):
    """ Check that file upload is working and file is shown in file list endpoint. """

    username, access_token = logged_user
    headers = {"Authorization": f"Bearer {access_token}"}

    with test_file.open() as f:
        files = files_factory(f, test_file)
        response = await client.post("/files/upload", files=files, headers=headers)

    assert response.status_code == 200

    upload_result = response.json()
    assert isinstance(upload_result, dict)
    uid = upload_result["uid"]

    def check_file_response_model(file_model: dict):
        assert str(UUID(file_model["uid"])) == uid
        assert file_model["filename"] == expected_name
        assert file_model["owner"] == username
        assert file_model["content_type"] == expected_content_type

    check_file_response_model(upload_result)

    response = await client.get("/files/", headers=headers)
    assert response.status_code == 200

    file_list = response.json()
    assert isinstance(file_list, list)
    assert len(file_list) == 1

    check_file_response_model(file_list[0])

    saved_file = files_dir / uid
    assert saved_file.exists()
    assert saved_file.read_text() == content == test_file.read_text()

    assert list(i.name for i in files_dir.iterdir()) == [uid]

    response = await client.get(f"/files/download/{uid}", headers=headers)
    assert response.status_code == 200
    assert response.text == test_file.read_text()
    assert response.headers["content-disposition"] == f'attachment; filename="{expected_name}"'

    response = await client.delete(f"/files/delete/{uid}", headers=headers)
    assert response.status_code == 200
    assert not saved_file.exists()


@pytest.fixture()
async def upload_file(logged_user, client, test_file):
    username, access_token = logged_user
    headers = {"Authorization": f"Bearer {access_token}"}

    with test_file.open() as f:
        response = await client.post("/files/upload", files=dict(file=f), headers=headers)

    assert response.status_code == 200
    return response.json()


@pytest.mark.asyncio
async def test_file_upload_result(upload_file: dict):
    assert isinstance(upload_file, dict)
    uid = upload_file["uid"]
    assert str(UUID(uid)) == uid
    assert upload_file["filename"] == "test-file.txt"
    assert upload_file["owner"] == "test_user"
    assert upload_file["content_type"] == "text/plain"


@pytest.mark.asyncio
async def test_file_list(logged_user, upload_file: dict, client: AsyncClient):
    username, access_token = logged_user
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get("/files/", headers=headers)
    assert response.status_code == 200

    file_list = response.json()
    assert isinstance(file_list, list)
    assert len(file_list) == 1
    file_model = file_list[0]

    uid = file_model["uid"]
    assert str(UUID(uid)) == uid
    assert file_model["filename"] == "test-file.txt"
    assert file_model["owner"] == "test_user"
    assert file_model["content_type"] == "text/plain"


@pytest.mark.asyncio
async def test_file_saved_on_filesystem(files_dir: Path, upload_file: dict, test_file: Path):
    uid = upload_file["uid"]
    saved_file = files_dir / uid
    assert saved_file.exists()
    assert saved_file.read_text() == test_file.read_text() == content
    assert list(i.name for i in files_dir.iterdir()) == [uid]


@pytest.mark.asyncio
async def test_file_download(logged_user, client: AsyncClient, upload_file: dict, test_file: Path):
    username, access_token = logged_user
    headers = {"Authorization": f"Bearer {access_token}"}
    uid = upload_file["uid"]
    response = await client.get(f"/files/download/{uid}", headers=headers)
    assert response.status_code == 200
    assert response.text == test_file.read_text() == content
    assert response.headers["content-disposition"] == f'attachment; filename="test-file.txt"'


@pytest.mark.asyncio
async def test_file_delete(logged_user, client: AsyncClient, upload_file: dict, files_dir: Path):
    username, access_token = logged_user
    headers = {"Authorization": f"Bearer {access_token}"}
    uid = upload_file["uid"]
    saved_file = files_dir / uid
    assert saved_file.exists()

    response = await client.delete(f"/files/delete/{uid}", headers=headers)
    assert response.status_code == 200
    assert not saved_file.exists()

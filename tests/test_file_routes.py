from pathlib import Path
from typing import Callable
from uuid import UUID

import pytest
from databases import Database
from httpx import AsyncClient
from sqlalchemy import func, select

from cyberbox.models import files


def simple_files(file, path):
    return dict(file=file)


def with_content_type(file, path):
    return dict(file=(path.name, file, "text/plain"))


def with_another_name(file, path):
    return dict(file=("another.name.tar.gz", file))


def with_content_type_and_another_name(file, path):
    return dict(file=("another.name.tar.gz", file, "text/plain"))


def check_file_response_model(
    file_model: dict,
    expected_name="test-file.txt",
    username="test_user",
    expected_content_type="text/plain",
):
    uid = file_model["uid"]
    assert str(UUID(uid)) == uid
    assert file_model["filename"] == expected_name
    assert file_model["owner"] == username
    assert file_model["content_type"] == expected_content_type


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
):
    """ Check that file upload is working and file is shown in file list endpoint. """

    username, access_token, headers = logged_user

    with test_file.open() as f:
        files_dict = files_factory(f, test_file)
        response = await client.post("/files/upload", files=files_dict, headers=headers)

    assert response.status_code == 200

    upload_result = response.json()
    assert isinstance(upload_result, dict)

    check_file_response_model(
        upload_result, expected_name=expected_name, expected_content_type=expected_content_type
    )

    response = await client.get("/files/", headers=headers)
    assert response.status_code == 200

    file_list = response.json()
    assert isinstance(file_list, list)
    assert len(file_list) == 1
    check_file_response_model(
        file_list[0], expected_name=expected_name, expected_content_type=expected_content_type
    )


@pytest.mark.asyncio
async def test_file_upload_result(upload_file: dict):
    """ Check json response after file upload. """
    assert isinstance(upload_file, dict)
    check_file_response_model(upload_file)


@pytest.mark.asyncio
async def test_file_list(logged_user, upload_file: dict, client: AsyncClient):
    """ Check json response in file list. """
    username, access_token, headers = logged_user
    response = await client.get("/files/", headers=headers)
    assert response.status_code == 200

    file_list = response.json()
    assert isinstance(file_list, list)
    assert len(file_list) == 1
    check_file_response_model(file_list[0])


@pytest.mark.asyncio
async def test_file_saved_on_filesystem(files_dir: Path, upload_file: dict, test_file: Path):
    """ Check that uploaded file exist on filesystem. """
    uid = upload_file["uid"]
    saved_file = files_dir / uid
    assert saved_file.exists()
    assert saved_file.read_text() == test_file.read_text()
    assert list(i.name for i in files_dir.iterdir()) == [uid]


@pytest.mark.asyncio
async def test_file_download(logged_user, client: AsyncClient, upload_file: dict, test_file: Path):
    """ Check file can be downloaded and content is valid. """
    username, access_token, headers = logged_user
    uid = upload_file["uid"]
    response = await client.get(f"/files/download/{uid}", headers=headers)
    assert response.status_code == 200
    assert response.text == test_file.read_text()
    assert response.headers["content-disposition"] == f'attachment; filename="test-file.txt"'


@pytest.mark.asyncio
async def test_file_delete(
    logged_user, client: AsyncClient, upload_file: dict, files_dir: Path, db: Database
):
    """ Check file can be deleted from db and from filesystem. """
    username, access_token, headers = logged_user
    uid = upload_file["uid"]
    saved_file = files_dir / uid
    assert saved_file.exists()
    assert await db.execute(select([func.count()]).select_from(files)) == 1

    response = await client.delete(f"/files/delete/{uid}", headers=headers)
    assert response.status_code == 200
    assert not saved_file.exists()

    assert await db.execute(select([func.count()]).select_from(files)) == 0

from pathlib import Path
from typing import Callable
from uuid import UUID

import pytest
from starlette.testclient import TestClient


@pytest.fixture()
def test_file(tmp_path):
    file = tmp_path / "test-file.txt"
    file.write_text("some\ncontext")
    return file


def simple_files(file, path):
    return dict(file=file)


def with_content_type(file, path):
    return dict(file=(path.name, file, "text/plain"))


def with_content_type_and_another_name(file, path):
    return dict(file=("another.name.tar.gz", file, "text/plain"))


@pytest.mark.parametrize(
    "files_factory, expected_name, expected_content_type",
    [
        [simple_files, "test-file.txt", ""],
        [with_content_type, "test-file.txt", "text/plain"],
        [with_content_type_and_another_name, "another.name.tar.gz", "text/plain"],
    ],
)
def test_file_upload(
    client: TestClient,
    test_file: Path,
    logged_user,
    files_factory: Callable,
    expected_name,
    expected_content_type,
):
    """ Check that file upload is working and file is shown in file list endpoint. """

    username, access_token = logged_user
    headers = {"Authorization": f"Bearer {access_token}"}

    with test_file.open() as f:
        files = files_factory(f, test_file)
        response = client.post("/files/upload", files=files, headers=headers)

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

    response = client.get("/files/", headers=headers)
    assert response.status_code == 200

    file_list = response.json()
    assert isinstance(file_list, list)
    assert len(file_list) == 1

    check_file_response_model(file_list[0])

from contextlib import nullcontext

import pytest
from pydantic import ValidationError

from cyberbox.config import parse_config
from cyberbox.const import CONFIG_ENV_NAME
from cyberbox.env import Env


@pytest.fixture()
def config_factory(tmp_path, monkeypatch):
    config_file = tmp_path / "test_config"
    monkeypatch.setenv(CONFIG_ENV_NAME, str(config_file))

    def factory(content: str):
        config_file.write_text(content)

    return factory


@pytest.fixture()
def files_dir(tmp_path):
    files_dir = tmp_path / "files-dir"
    files_dir.mkdir()
    return files_dir


@pytest.mark.parametrize(
    "env_value, force_rollback, expectation",
    [
        ["test", False, nullcontext()],
        ["test", True, nullcontext()],
        ["dev", False, nullcontext()],
        ["dev", True, pytest.raises(ValidationError)],
        ["prod", True, pytest.raises(ValidationError)],
        ["prod", False, nullcontext()],
        ["unknown", False, pytest.raises(ValidationError)],
        ["", False, pytest.raises(ValidationError)],
    ],
)
def test_config(config_factory, env_value, force_rollback, expectation, files_dir):
    config_factory(
        f"""
    environment: {env_value}
    jwt:
        secret_key: '02928b262b416dca50816d10162151ef0af0f625adb47d73a1526a3630ca8f1f'
    database:
        url: postgresql://user:pass@localhost:1234
        force_rollback: {force_rollback}
    files_dir: {files_dir}
    """
    )
    with expectation:
        config = parse_config()
        assert isinstance(config.environment, Env)

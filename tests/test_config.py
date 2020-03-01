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


@pytest.mark.parametrize(
    "env_value, expectation",
    [
        ["test", nullcontext()],
        ["dev", nullcontext()],
        ["prod", nullcontext()],
        ["unknown", pytest.raises(ValidationError)],
        ["", pytest.raises(ValidationError)],
    ],
)
def test_config(config_factory, env_value, expectation):
    config_factory(
        f"""
    environment: {env_value}
    database:
        url: postgresql://user:pass@localhost:1234
    """
    )
    with expectation:
        config = parse_config()
        assert isinstance(config.environment, Env)

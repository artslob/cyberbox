import os
from pathlib import Path
from typing import Callable

import yaml
from pydantic import BaseModel, PostgresDsn

from cyberbox.const import CONFIG_ENV_NAME
from cyberbox.env import Env


class DatabaseConfig(BaseModel):
    url: PostgresDsn


class Config(BaseModel):
    environment: Env
    database: DatabaseConfig


def default_loader(file: Path) -> dict:
    """ Default loader parses .yaml config file. """
    result = yaml.safe_load(file.read_text())
    if not isinstance(result, dict):
        raise ValueError("Loaded config is not a mapping")
    return result


def parse_config(
    env_name: str = CONFIG_ENV_NAME, loader: Callable[[Path], dict] = default_loader
) -> Config:
    """ Parses file and returns config. Filename is provided by environment variable. """

    config_file_path = os.environ.get(env_name)
    if not config_file_path:
        msg = f"Provide environment variable with name {env_name!r} and value - path to config file"
        raise ValueError(msg)

    config_file = Path(config_file_path)
    if not config_file.is_file():
        raise ValueError(f"File {config_file_path} does not exist or not a file")

    config = loader(config_file)
    return Config.parse_obj(config)

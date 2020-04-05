import os
from pathlib import Path
from typing import Callable

import yaml
from pydantic import BaseModel, DirectoryPath, Field, PostgresDsn, root_validator

from cyberbox.const import CONFIG_ENV_NAME
from cyberbox.env import Env


class DatabaseConfig(BaseModel):
    url: PostgresDsn
    force_rollback: bool = False


class Config(BaseModel):
    environment: Env
    secret_key: str = Field(..., min_length=10)
    jwt_algorithm: str = "HS256"
    database: DatabaseConfig
    files_dir: DirectoryPath

    @root_validator
    def check_force_rollback_only_in_testing(cls, values: dict):
        # fields didnt pass validation
        if "environment" not in values or "database" not in values:
            return values
        if values["environment"] is not Env.test and values["database"].force_rollback:
            raise ValueError("force_rollback should be enabled only in testing environment")
        return values


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

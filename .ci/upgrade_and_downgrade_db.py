#!/usr/bin/env python
import os

from alembic import command
from alembic.config import Config

from cyberbox.const import CYBERBOX_TEST_DB_URL


def main():
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", "cyberbox:migrations")
    alembic_cfg.set_main_option("sqlalchemy.url", os.environ[CYBERBOX_TEST_DB_URL].strip())

    alembic_cfg.print_stdout("Upgrade to head:")
    command.upgrade(alembic_cfg, "head")
    command.history(alembic_cfg, indicate_current=True)

    alembic_cfg.print_stdout("\nDowngrade to base:")
    command.downgrade(alembic_cfg, "base")
    command.history(alembic_cfg, indicate_current=True)


if __name__ == "__main__":
    main()

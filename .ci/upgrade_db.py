#!/usr/bin/env python

import argparse
import os

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, drop_database

from cyberbox.const import CYBERBOX_TEST_DB_URL
from cyberbox.orm import metadata


def parse_args():
    parser = argparse.ArgumentParser(description="Upgrade database.")
    parser.add_argument("--method", choices=["meta", "migration"], required=True)
    return parser.parse_args()


def main():
    args = parse_args()

    db_url = os.environ[CYBERBOX_TEST_DB_URL].strip()
    drop_database(db_url)
    create_database(db_url)
    engine = create_engine(db_url)

    if args.method == "meta":
        print(len(metadata.tables))
        metadata.create_all(engine)
        return

    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", "cyberbox:migrations")
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    command.upgrade(alembic_cfg, "head")
    engine.execute("DROP TABLE IF EXISTS alembic_version CASCADE;")


if __name__ == "__main__":
    main()
    print("upgraded successfully")

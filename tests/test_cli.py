import pytest
from databases import Database

from cyberbox import orm
from cyberbox.__main__ import __create_admin
from cyberbox.utils import exec_count


@pytest.mark.asyncio
async def test_cli_create_superuser(db: Database):
    await __create_admin(db, "qwe", "123")
    query = orm.User.select().where(orm.User.c.is_admin.is_(True))
    assert await exec_count(db, query.alias()) == 1

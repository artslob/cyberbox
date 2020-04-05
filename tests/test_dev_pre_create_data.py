import pytest
from databases import Database
from sqlalchemy import func, select

from cyberbox import orm
from cyberbox.dev.pre_create_data import create_data


@pytest.mark.asyncio
async def test_pre_create_data(db: Database):
    await create_data(db)

    assert await db.execute(select([func.count()]).select_from(orm.User)) == 1

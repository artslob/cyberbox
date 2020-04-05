import pytest
from databases import Database
from sqlalchemy import func, select

from cyberbox import orm


@pytest.mark.asyncio
async def test_user_created(db: Database, create_users):
    assert await db.execute(select([func.count()]).select_from(orm.users)) == 3


@pytest.mark.asyncio
async def test_files_created(db: Database, create_files):
    assert await db.execute(select([func.count()]).select_from(orm.files)) == 80

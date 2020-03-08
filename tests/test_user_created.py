import pytest
from databases import Database
from sqlalchemy import func, select

from cyberbox.models import users


@pytest.mark.asyncio
async def test_user_created(db: Database, create_user):
    assert await db.execute(select([func.count()]).select_from(users)) == 1

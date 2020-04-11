import asyncio

import arrow
from databases import Database

from cyberbox import orm
from cyberbox.routes.auth import crypt_context


async def pre_create_data():
    """
    Create some data for development purposes.
    Upgrade database using migration before running this script.
    """
    from cyberbox.asgi import app

    db: Database = app.state.db

    async with db:
        async with db.transaction():
            await create_data(db)


async def create_data(db: Database):
    values = dict(
        uid="b3b4a8a3-d179-4f10-808d-12980175beb0",
        username="qwe",
        disabled=False,
        hashed_password=crypt_context.hash("123"),
        created=arrow.utcnow().datetime,
        is_admin=True,
    )
    await db.execute(orm.User.insert(values=values))


if __name__ == "__main__":
    asyncio.run(pre_create_data())

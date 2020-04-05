import asyncio

import arrow
import sqlalchemy
from databases import Database
from sqlalchemy_utils import create_database, drop_database

from cyberbox import orm
from cyberbox.routes.auth import crypt_context


async def pre_create_data():
    from cyberbox.asgi import app

    db: Database = app.state.db
    db_url = app.state.cfg.database.url
    engine = sqlalchemy.create_engine(db_url)

    drop_database(db_url)
    create_database(db_url)
    orm.metadata.create_all(engine)

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
    )
    await db.execute(orm.User.insert(values=values))


if __name__ == "__main__":
    asyncio.run(pre_create_data())

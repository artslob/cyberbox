import asyncio

import sqlalchemy
from databases import Database
from sqlalchemy_utils import create_database, drop_database

from cyberbox.asgi import app
from cyberbox.models import metadata, users


async def pre_create_data():
    database: Database = app.state.db
    db_url = app.state.cfg.database.url
    engine = sqlalchemy.create_engine(db_url)

    drop_database(db_url)
    create_database(db_url)
    metadata.create_all(engine)

    await database.connect()
    async with database.transaction():
        values = dict(
            uid="b3b4a8a3-d179-4f10-808d-12980175beb0",
            username="qwe",
            disabled=False,
            hashed_password="$2b$12$WCRPaoVwPNmhUXHmHoAkDOrsy4oFnfp/Ozts/iEVoaL2onpsrfZEO",
        )
        await database.execute(users.insert(values=values))

    await database.disconnect()


asyncio.run(pre_create_data())

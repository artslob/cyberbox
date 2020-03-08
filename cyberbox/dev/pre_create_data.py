import asyncio

import sqlalchemy
from databases import Database

from cyberbox.asgi import app
from cyberbox.models import metadata, users


async def pre_create_data():
    database: Database = app.db
    engine = sqlalchemy.create_engine(app.cfg.database.url)
    metadata.drop_all(engine)
    metadata.create_all(engine)
    await database.connect()
    values = dict(
        uid="b3b4a8a3-d179-4f10-808d-12980175beb0",
        username="qwe",
        disabled=False,
        hashed_password="$2b$12$WCRPaoVwPNmhUXHmHoAkDOrsy4oFnfp/Ozts/iEVoaL2onpsrfZEO",
    )
    await database.execute(users.insert(values=values))


asyncio.run(pre_create_data())

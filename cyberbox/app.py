import sqlalchemy
from databases import Database
from fastapi import FastAPI

from .models import metadata, users
from .routes import auth, root, test


def create_app(database_url="postgresql://devuser:devpass@localhost:5432/cyberbox-db") -> FastAPI:
    app = FastAPI()

    database = Database(database_url)
    app.db = database

    @app.on_event("startup")
    async def startup():
        engine = sqlalchemy.create_engine(database_url)
        metadata.drop_all(engine)
        metadata.create_all(engine)
        await database.connect()
        values = dict(uid="b3b4a8a3-d179-4f10-808d-12980175beb0", username="qwe", disabled=False)
        await database.execute(users.insert(values=values))

    @app.on_event("shutdown")
    async def shutdown():
        await database.disconnect()

    app.include_router(root.router)
    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(test.router, prefix="/test", tags=["test"])

    return app

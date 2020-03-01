import sqlalchemy
from databases import Database
from fastapi import FastAPI

from cyberbox.config import parse_config
from cyberbox.models import metadata, users
from cyberbox.routes import auth, files, root, test


def create_app() -> FastAPI:
    app = FastAPI()

    config = parse_config()
    app.cfg = config

    database = Database(config.database.url)
    app.db = database

    @app.on_event("startup")
    async def startup():
        engine = sqlalchemy.create_engine(config.database.url)
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

    @app.on_event("shutdown")
    async def shutdown():
        await database.disconnect()

    app.include_router(root.router)
    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(files.router, prefix="/files", tags=["files"])
    app.include_router(test.router, prefix="/test", tags=["test"])

    return app

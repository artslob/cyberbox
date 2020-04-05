from databases import Database
from fastapi import FastAPI

from cyberbox.config import parse_config
from cyberbox.routes import auth, files, links


def create_app() -> FastAPI:
    app = FastAPI()

    config = parse_config()
    app.state.cfg = config

    database = Database(config.database.url, force_rollback=config.database.force_rollback)
    app.state.db = database

    @app.on_event("startup")
    async def startup():
        await database.connect()

    @app.on_event("shutdown")
    async def shutdown():
        await database.disconnect()

    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(files.router, prefix="/file", tags=["file"])
    app.include_router(links.router, prefix="/link", tags=["link"])

    return app

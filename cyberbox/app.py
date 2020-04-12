from databases import Database
from fastapi import Depends, FastAPI

from cyberbox.config import parse_config
from cyberbox.dependency import get_admin_user, get_current_user
from cyberbox.routes import admin, auth, files, links


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

    app.include_router(
        admin.router, prefix="/admin", tags=["admin"], dependencies=[Depends(get_admin_user)]
    )
    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(
        files.router, prefix="/file", tags=["file"], dependencies=[Depends(get_current_user)]
    )
    app.include_router(links.router, prefix="/link", tags=["link"])

    return app

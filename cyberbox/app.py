from fastapi import FastAPI

from .routes import auth, root, test


def create_app() -> FastAPI:
    app = FastAPI()

    app.include_router(root.router)
    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(test.router, prefix="/test", tags=["test"])

    return app

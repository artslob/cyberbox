import jwt
from databases import Database
from fastapi import Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from starlette import status
from starlette.requests import Request

from cyberbox import orm
from cyberbox.config import Config
from cyberbox.models import FilterParams, UserModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_db(request: Request):
    db: Database = request.app.state.db
    async with db.transaction():
        yield db


async def get_config(request: Request) -> Config:
    return request.app.state.cfg


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Database = Depends(get_db),
    cfg: Config = Depends(get_config),
) -> UserModel:
    try:
        payload = jwt.decode(token, cfg.jwt.secret_key, algorithms=[cfg.jwt.algorithm])
    except PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Could not validate access token")

    row = await db.fetch_one(orm.User.select().where(orm.User.c.username == payload.get("sub")))
    if row is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User does not exist")

    user = UserModel.parse_obj(row)
    if user.disabled:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "User is disabled")

    return user


async def get_admin_user(user: UserModel = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "you must be admin to access this endpoint")

    return user


async def get_filter_params(
    page: int = Query(1, alias="_page", ge=1), limit: int = Query(20, alias="_limit", ge=1, le=500)
) -> FilterParams:
    return FilterParams(page=page, limit=limit)

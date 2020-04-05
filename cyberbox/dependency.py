import jwt
from databases import Database
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from cyberbox import orm
from cyberbox.config import Config
from cyberbox.models import UserModel

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
        payload = jwt.decode(token, cfg.secret_key, algorithms=[cfg.jwt_algorithm])
    except PyJWTError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Could not validate access token"
        )

    row = await db.fetch_one(orm.User.select().where(orm.User.c.username == payload.get("sub")))
    if row is None:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="User does not exist")

    user = UserModel.parse_obj(row)
    if user.disabled:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="User is disabled")

    return user

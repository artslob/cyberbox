from typing import Optional

import arrow
import jwt
from databases import Database
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from cyberbox import orm
from cyberbox.config import Config
from cyberbox.dependency import get_config, get_current_user, get_db
from cyberbox.models import TokenModel, UserModel

router = APIRouter()

crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def authenticate_user(username, password, db: Database) -> Optional[UserModel]:
    row = await db.fetch_one(orm.User.select().where(orm.User.c.username == username))
    if not row or not crypt_context.verify(password, row["hashed_password"]):
        return None
    return UserModel.parse_obj(row)


def create_access_token(username: str, cfg: Config) -> str:
    exp_in_minutes = cfg.jwt.access_token_expire_minutes
    exp = arrow.utcnow().shift(minutes=exp_in_minutes).datetime
    data = dict(sub=username, exp=exp, iat=arrow.utcnow().datetime)
    return jwt.encode(data, cfg.jwt.secret_key, cfg.jwt.algorithm)


@router.post("/login", response_model=TokenModel)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Database = Depends(get_db),
    cfg: Config = Depends(get_config),
):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Incorrect user or password")

    if user.disabled:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="User is disabled")

    access_token = create_access_token(user.username, cfg)
    return TokenModel(access_token=access_token, token_type="bearer")


# TODO register


@router.get("/profile", response_model=UserModel)
async def profile(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    return current_user

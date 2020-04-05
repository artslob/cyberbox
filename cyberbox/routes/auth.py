from copy import deepcopy
from datetime import datetime, timedelta
from typing import Optional

import jwt
from databases import Database
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from cyberbox import orm
from cyberbox.config import Config
from cyberbox.models import TokenModel, UserModel
from cyberbox.routes.common import ALGORITHM, get_config, get_current_user, get_db

ACCESS_TOKEN_EXPIRE_MINUTES = 60

router = APIRouter()

crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def authenticate_user(username, password, db: Database) -> Optional[UserModel]:
    row = await db.fetch_one(orm.User.select().where(orm.User.c.username == username))
    if not row or not crypt_context.verify(password, row["hashed_password"]):
        return None
    return UserModel.parse_obj(row)


def create_access_token(data: dict, secret_key: str) -> str:
    data = deepcopy(data)
    data["exp"] = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(data, secret_key, ALGORITHM)


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

    token = create_access_token(dict(sub=user.username), cfg.secret_key)
    return TokenModel(access_token=token, token_type="bearer")


@router.get("/logout")
async def logout():
    return "todo logout"


@router.get("/profile", response_model=UserModel)
async def profile(current_user: UserModel = Depends(get_current_user)):
    return current_user

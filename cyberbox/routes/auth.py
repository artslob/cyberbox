from typing import Optional
from uuid import uuid4

import arrow
import jwt
from databases import Database
from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy import exists, select
from starlette import status

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
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect user or password")

    if user.disabled:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "User is disabled")

    access_token = create_access_token(user.username, cfg)
    return TokenModel(access_token=access_token, token_type="bearer")


@router.post("/register")
async def register(
    db: Database = Depends(get_db),
    username: str = Form(..., min_length=3),
    password1: str = Form(..., min_length=3),
    password2: str = Form(..., min_length=3),
):
    query = select([exists().where(orm.User.c.username == username)])
    is_exist = await db.execute(query)

    if is_exist:
        detail = f"user with username {username!r} already exists"
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail)

    if password1 != password2:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "submitted passwords are not equal")

    values = dict(
        uid=uuid4(),
        username=username,
        disabled=True,  # TODO: config param 'disabled_by_default'
        hashed_password=crypt_context.hash(password1),
        created=arrow.utcnow().datetime,
        is_admin=False,
    )
    await db.execute(orm.User.insert(values=values))


@router.get("/profile", response_model=UserModel)
async def profile(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    return current_user

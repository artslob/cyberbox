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
    query = orm.User.select().where(orm.User.c.username == form_data.username)
    row = await db.fetch_one(query)
    if not row or not crypt_context.verify(form_data.password, row["hashed_password"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect user or password")

    user = UserModel.parse_obj(row)

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
        disabled=False,  # TODO: config param 'disabled_by_default'
        hashed_password=crypt_context.hash(password1),
        created=arrow.utcnow().datetime,
        is_admin=False,
    )
    await db.execute(orm.User.insert(values=values))


@router.get("/profile", response_model=UserModel)
async def profile(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    return current_user

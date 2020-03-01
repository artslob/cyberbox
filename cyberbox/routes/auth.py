from copy import deepcopy
from datetime import datetime, timedelta
from typing import Optional

import jwt
from databases import Database
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel
from starlette.status import HTTP_401_UNAUTHORIZED

from cyberbox.models import users
from cyberbox.routes.common import ALGORITHM, SECRET_KEY, User, get_current_user, get_db

ACCESS_TOKEN_EXPIRE_MINUTES = 60

router = APIRouter()

crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Token(BaseModel):
    access_token: str
    token_type: str


async def authenticate_user(username, password, db: Database) -> Optional[User]:
    row = await db.fetch_one(users.select().where(users.c.username == username))
    if not row or not crypt_context.verify(password, row["hashed_password"]):
        return None
    return User.parse_obj(row)


def create_access_token(data: dict):
    data = deepcopy(data)
    data["exp"] = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(data, SECRET_KEY, ALGORITHM)


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Database = Depends(get_db)):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Incorrect user or password")

    token = create_access_token(dict(sub=user.username))
    return Token(access_token=token, token_type="bearer")


@router.get("/logout")
async def logout():
    return "todo logout"


@router.get("/profile", response_model=User)
async def profile(current_user: User = Depends(get_current_user)):
    return current_user

from copy import deepcopy
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

import jwt
from databases import Database
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import PyJWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from cyberbox.models import users

SECRET_KEY = "55aeab38-2e3d-490d-bcdb-b16cd303ef1f"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

router = APIRouter()


class User(BaseModel):
    uid: UUID = None
    username: str
    disabled: bool = False


crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class Token(BaseModel):
    access_token: str
    token_type: str


async def get_db(request: Request) -> Database:
    return request.app.db


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


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Database = Depends(get_db)
) -> User:

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except PyJWTError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Could not validate access token"
        )

    row = await db.fetch_one(users.select().where(users.c.username == payload.get("sub")))
    if row is None:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="User does not exist")

    user = User.parse_obj(row)
    if user.disabled:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="User is disabled")

    return user


@router.get("/profile", response_model=User)
async def profile(current_user: User = Depends(get_current_user)):
    return current_user

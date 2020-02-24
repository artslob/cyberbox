from copy import deepcopy
from datetime import datetime, timedelta
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


class FakeUser(BaseModel):
    username: str
    disabled: bool = False
    hashed_password: str


fake_users = {
    # pass is 123
    "qwe": FakeUser(
        username="qwe",
        hashed_password="$2b$12$WCRPaoVwPNmhUXHmHoAkDOrsy4oFnfp/Ozts/iEVoaL2onpsrfZEO",
    ),
    "test": FakeUser(
        username="test",
        hashed_password="$2b$12$dOUPh.YsYeAfV61S6muToOWJqvJvCVKL99uwBb5a/venqht1m0PZi",
        disabled=True,
    ),
}

crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class Token(BaseModel):
    access_token: str
    token_type: str


def authenticate_user(username, password):
    user = fake_users.get(username)
    if not user:
        return None
    if not crypt_context.verify(password, user.hashed_password):
        print(crypt_context.hash(password))
        return None
    return user


def create_access_token(data: dict):
    data = deepcopy(data)
    data["exp"] = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(data, SECRET_KEY, ALGORITHM)


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Incorrect user or password")

    token = create_access_token(dict(sub=user.username))
    return Token(access_token=token, token_type="bearer")


@router.get("/logout")
async def logout():
    return "todo logout"


async def get_db(request: Request) -> Database:
    return request.app.db


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Database = Depends(get_db)
) -> User:
    validation_exc = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED, detail="Could not validate access token"
    )
    disabled_exc = HTTPException(status_code=HTTP_403_FORBIDDEN, detail="User is disabled")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except PyJWTError:
        raise validation_exc

    username: str = payload.get("sub")
    record = await db.fetch_one(users.select().where(users.c.username == username))
    if record is None:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="User does not exist")
    user = User(**{k: v for k, v in record.items()})
    if user.disabled:
        raise disabled_exc
    return user


@router.get("/profile", response_model=User)
async def profile(current_user: User = Depends(get_current_user)):
    return current_user

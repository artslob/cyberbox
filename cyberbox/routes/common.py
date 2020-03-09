from uuid import UUID

import jwt
from databases import Database
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from pydantic import BaseModel
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from cyberbox.models import users

SECRET_KEY = "55aeab38-2e3d-490d-bcdb-b16cd303ef1f"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class User(BaseModel):
    uid: UUID = None
    username: str
    disabled: bool = False


async def get_db(request: Request):
    db: Database = request.app.state.db
    async with db.transaction():
        yield db


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

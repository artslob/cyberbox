from uuid import UUID

from databases import Database
from fastapi import APIRouter, Depends, HTTPException
from pydantic.main import BaseModel
from starlette import status

from cyberbox import orm
from cyberbox.dependency import get_db, get_filter_params
from cyberbox.models import FilterParams, Page, UserModel
from cyberbox.pagination import pagination

router = APIRouter()


@router.get("/user/", response_model=Page[UserModel])
async def get_user_list(
    db: Database = Depends(get_db), params: FilterParams = Depends(get_filter_params),
):
    query = orm.User.select()
    return await pagination(query, orm.User, Page[UserModel], db, params)


class UpdateUserModel(BaseModel):
    disabled: bool
    is_admin: bool


@router.put("/user/{user_uid}")
async def update_user(
    *, user_uid: UUID, db: Database = Depends(get_db), update_data: UpdateUserModel
):
    query = orm.User.update().where(orm.User.c.uid == user_uid).returning(orm.User.c.uid)
    updated_uid = await db.execute(query, update_data.dict())
    if user_uid != updated_uid:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"user with uid {str(user_uid)!r} not exist")

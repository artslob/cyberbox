from databases import Database
from fastapi import APIRouter, Depends

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


@router.put("/user/{user_uid}")
async def update_user():
    pass

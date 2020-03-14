import secrets
from uuid import UUID

from databases import Database
from fastapi import APIRouter, Depends, HTTPException
from pydantic.main import BaseModel
from starlette.status import HTTP_404_NOT_FOUND

from cyberbox.models import files, links
from cyberbox.routes.common import User, get_current_user, get_db

router = APIRouter()


class Link(BaseModel):
    uid: UUID
    link: str
    is_onetime: bool
    visited_count: int


@router.post("/{file_uid}", response_model=Link)
async def create_link(
    *,
    file_uid: UUID,
    user: User = Depends(get_current_user),
    db: Database = Depends(get_db),
    is_onetime: bool = False,
):
    query = files.select().where((files.c.owner == user.username) & (files.c.uid == file_uid))
    row = await db.fetch_one(query)
    if not row:
        detail = f"File with uuid {str(file_uid)!r} not found"
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=detail)

    values = dict(
        uid=file_uid, link=secrets.token_urlsafe(16), is_onetime=is_onetime, visited_count=0
    )
    await db.execute(links.insert().values(values))
    return values


@router.get("/{link}/info", response_model=Link)
async def link_info(link: str, db: Database = Depends(get_db)):
    row = await db.fetch_one(links.select().where(links.c.link == link))
    if not row:
        detail = f"Link with value {link!r} does not exist"
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=detail)

    return row


@router.get("/")
async def download_file_by_link():
    pass


# TODO download by one time link


@router.delete("/")
async def delete_link():
    pass

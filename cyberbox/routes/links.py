import secrets
from uuid import UUID

from databases import Database
from fastapi import APIRouter, Depends, HTTPException
from pydantic.main import BaseModel
from sqlalchemy import select
from starlette.responses import FileResponse
from starlette.status import HTTP_404_NOT_FOUND

from cyberbox.config import Config
from cyberbox.models import files, links
from cyberbox.routes.common import User, get_config, get_current_user, get_db
from cyberbox.routes.files import FileModel

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
    # TODO change select all fields to check existence
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


@router.get("/{link}", response_model=FileModel)
async def download_file_by_link(
    link: str, db: Database = Depends(get_db), cfg: Config = Depends(get_config)
):
    join = files.join(links, links.c.link == link)
    query = files.select().select_from(join)
    row = await db.fetch_one(query)
    if not row:
        detail = "Link does not exist"
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=detail)

    file_path = cfg.files_dir / str(row["uid"])
    return FileResponse(str(file_path), filename=row["filename"])


# TODO download by one time link


@router.delete("/{link}")
async def delete_link(
    link: str, db: Database = Depends(get_db), user: User = Depends(get_current_user)
):
    query = (
        links.delete()
        .where(links.c.link == link)
        .where(links.c.uid == select([files.c.uid]).where(files.c.owner == user.username))
        .returning(links.c.link)
    )
    deleted_link = await db.execute(query)
    if deleted_link != link:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Link {link} does not exist")

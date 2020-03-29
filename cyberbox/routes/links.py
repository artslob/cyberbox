import secrets
from datetime import datetime
from uuid import UUID

import arrow
from databases import Database
from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic.main import BaseModel
from sqlalchemy import exists, select
from starlette.responses import FileResponse
from starlette.status import HTTP_404_NOT_FOUND

from cyberbox.config import Config
from cyberbox.models import files, links
from cyberbox.routes.common import User, get_config, get_current_user, get_db

router = APIRouter()


class Link(BaseModel):
    uid: UUID
    link: str
    is_onetime: bool
    created: datetime
    visited_count: int
    valid_until: datetime = None


# TODO link list endpoint


@router.post("/{file_uid}", response_model=Link)
async def create_link(
    *,
    file_uid: UUID,
    user: User = Depends(get_current_user),
    db: Database = Depends(get_db),
    is_onetime: bool = Body(False),
    valid_until: datetime = Body(None),
):
    query = select([exists().where((files.c.owner == user.username) & (files.c.uid == file_uid))])
    is_exist = await db.execute(query)
    if not is_exist:
        detail = f"File with uuid {str(file_uid)!r} not found"
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=detail)

    if valid_until is not None:
        valid_until = arrow.get(valid_until).datetime

    link = Link(
        uid=file_uid,
        link=secrets.token_urlsafe(16),
        is_onetime=is_onetime,
        created=arrow.utcnow().datetime,
        visited_count=0,
        valid_until=valid_until,
    )
    await db.execute(links.insert().values(link.dict()))
    return link


@router.get("/{link}/info", response_model=Link)
async def link_info(link: str, db: Database = Depends(get_db)):
    row = await db.fetch_one(links.select().where(links.c.link == link))
    if not row:
        detail = f"Link with value {link!r} does not exist"
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=detail)

    return row


@router.get("/{link}", response_class=FileResponse)
async def download_file_by_link(
    link: str, db: Database = Depends(get_db), cfg: Config = Depends(get_config)
):
    query = (
        files.select()
        .where(links.c.link == link)
        .where(links.c.valid_until.is_(None) | (links.c.valid_until >= arrow.utcnow().datetime))
        .select_from(files.join(links))
    )
    row = await db.fetch_one(query)
    if not row:
        detail = "Link does not exist"
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=detail)

    increment = links.update().where(links.c.link == link)
    await db.execute(increment, dict(visited_count=links.c.visited_count + 1))

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
        .where(links.c.uid.in_(select([files.c.uid]).where(files.c.owner == user.username)))
        .returning(links.c.link)
    )
    deleted_link = await db.execute(query)
    if deleted_link != link:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Link {link!r} does not exist")

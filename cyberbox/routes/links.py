import secrets
from datetime import datetime
from uuid import UUID

import arrow
from databases import Database
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy import exists, select
from starlette.responses import FileResponse
from starlette.status import HTTP_404_NOT_FOUND

from cyberbox import orm
from cyberbox.config import Config
from cyberbox.models import Link, User
from cyberbox.routes.common import get_config, get_current_user, get_db

router = APIRouter()


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
    query = select(
        [exists().where((orm.File.c.owner == user.username) & (orm.File.c.uid == file_uid))]
    )
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
    await db.execute(orm.Link.insert().values(link.dict()))
    return link


@router.get("/{link}/info", response_model=Link)
async def link_info(link: str, db: Database = Depends(get_db)):
    row = await db.fetch_one(orm.Link.select().where(orm.Link.c.link == link))
    if not row:
        detail = f"Link with value {link!r} does not exist"
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=detail)

    return row


@router.get("/{link}", response_class=FileResponse)
async def download_file_by_link(
    link: str, db: Database = Depends(get_db), cfg: Config = Depends(get_config)
):
    not_found = HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Link does not exist")

    query = (
        select([orm.File, orm.Link.c.is_onetime])
        .where(orm.Link.c.link == link)
        .where(
            orm.Link.c.valid_until.is_(None) | (orm.Link.c.valid_until >= arrow.utcnow().datetime)
        )
        .select_from(orm.File.join(orm.Link))
    )
    row = await db.fetch_one(query)
    if not row:
        raise not_found

    is_onetime = False
    if row[orm.Link.c.is_onetime]:
        is_onetime = True
        # set lock on row
        row = await db.fetch_one(query.with_for_update())

    if not row:
        raise not_found

    if is_onetime:
        delete = orm.Link.delete().where(orm.Link.c.link == link)
        await db.execute(delete)
    else:
        increment = orm.Link.update().where(orm.Link.c.link == link)
        await db.execute(increment, dict(visited_count=orm.Link.c.visited_count + 1))

    file_path = cfg.files_dir / str(row[orm.File.c.uid])
    return FileResponse(str(file_path), filename=row[orm.File.c.filename])


# TODO download by one time link


@router.delete("/{link}")
async def delete_link(
    link: str, db: Database = Depends(get_db), user: User = Depends(get_current_user)
):
    query = (
        orm.Link.delete()
        .where(orm.Link.c.link == link)
        .where(
            orm.Link.c.uid.in_(select([orm.File.c.uid]).where(orm.File.c.owner == user.username))
        )
        .returning(orm.Link.c.link)
    )
    deleted_link = await db.execute(query)
    if deleted_link != link:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Link {link!r} does not exist")

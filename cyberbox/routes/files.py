from typing import List
from uuid import UUID, uuid4

import aiofiles
import arrow
from databases import Database
from fastapi import Depends, File, HTTPException, UploadFile
from fastapi.routing import APIRouter
from starlette.responses import FileResponse, PlainTextResponse
from starlette.status import HTTP_404_NOT_FOUND

from cyberbox import orm
from cyberbox.config import Config
from cyberbox.dependency import get_config, get_current_user, get_db
from cyberbox.models import FileModel, UserModel

router = APIRouter()


@router.get("/", response_model=List[FileModel])
async def file_list(
    user: UserModel = Depends(get_current_user), db: Database = Depends(get_db),
):
    # TODO improve filter
    query = orm.File.select().where(orm.File.c.owner == user.username).limit(10)
    return await db.fetch_all(query)


@router.post("/upload", response_model=FileModel)
async def upload_file(
    user: UserModel = Depends(get_current_user),
    db: Database = Depends(get_db),
    cfg: Config = Depends(get_config),
    file: UploadFile = File(...),
):
    file_model = FileModel(
        uid=uuid4(),
        owner=user.username,
        filename=file.filename,
        content_type=file.content_type,
        created=arrow.utcnow().datetime,
    )
    await db.execute(orm.File.insert().values(file_model.dict()))

    file_path = cfg.files_dir / str(file_model.uid)
    async with aiofiles.open(file_path, "wb") as saved_file:
        await saved_file.write(await file.read())

    return file_model


@router.get("/{file_uid}", response_class=FileResponse)
async def download_file(
    file_uid: UUID,
    user: UserModel = Depends(get_current_user),
    db: Database = Depends(get_db),
    cfg: Config = Depends(get_config),
):
    query = orm.File.select().where(
        (orm.File.c.owner == user.username) & (orm.File.c.uid == file_uid)
    )
    row = await db.fetch_one(query)
    if not row:
        detail = f"File with uuid {str(file_uid)!r} not found"
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=detail)

    file_path = cfg.files_dir / str(file_uid)
    return FileResponse(str(file_path), filename=row["filename"])


@router.delete("/{file_uid}", response_class=PlainTextResponse)
async def delete_file(
    file_uid: UUID,
    user: UserModel = Depends(get_current_user),
    db: Database = Depends(get_db),
    cfg: Config = Depends(get_config),
):
    query = (
        orm.File.delete()
        .where((orm.File.c.owner == user.username) & (orm.File.c.uid == file_uid))
        .returning(orm.File.c.uid)
    )
    result = await db.execute(query)
    if not result:
        detail = f"File with uuid {str(file_uid)!r} not found"
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=detail)

    file_path = cfg.files_dir / str(file_uid)

    try:
        file_path.unlink()
    except FileNotFoundError:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"File with uuid {str(file_uid)!r} does not exist on filesystem",
        )

from typing import List
from uuid import UUID, uuid4

import aiofiles
from databases import Database
from fastapi import Depends, File, HTTPException, UploadFile
from fastapi.routing import APIRouter
from pydantic.main import BaseModel
from starlette.status import HTTP_404_NOT_FOUND

from cyberbox.config import Config
from cyberbox.models import files
from cyberbox.routes.common import User, get_config, get_current_user, get_db

router = APIRouter()


class FileModel(BaseModel):
    uid: UUID
    owner: str
    filename: str
    content_type: str


@router.get("/", response_model=List[FileModel])
async def file_list(
    user: User = Depends(get_current_user), db: Database = Depends(get_db),
):
    query = files.select().where(files.c.owner == user.username).limit(10)
    return await db.fetch_all(query)


@router.post("/upload", response_model=FileModel)
async def upload_file(
    user: User = Depends(get_current_user),
    db: Database = Depends(get_db),
    cfg: Config = Depends(get_config),
    file: UploadFile = File(...),
):
    file_uid = uuid4()
    file_path = cfg.files_dir / str(file_uid)
    async with aiofiles.open(file_path, "wb") as saved_file:
        await saved_file.write(await file.read())
    values = dict(
        uid=file_uid, owner=user.username, filename=file.filename, content_type=file.content_type
    )
    await db.execute(files.insert().values(values))
    return values


@router.get("/download/{file_uid}", response_model=FileModel)
async def download_file(
    file_uid: UUID, user: User = Depends(get_current_user), db: Database = Depends(get_db),
):
    query = files.select().where((files.c.owner == user.username) & (files.c.uid == file_uid))
    file = await db.fetch_one(query)
    if not file:
        detail = f"File with uuid {str(file_uid)!r} not found"
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=detail)

    return FileModel.parse_obj(file)

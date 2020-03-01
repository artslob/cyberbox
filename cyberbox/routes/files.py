from typing import List
from uuid import UUID, uuid4

from databases import Database
from fastapi import Depends, File, UploadFile
from fastapi.routing import APIRouter
from pydantic.main import BaseModel

from cyberbox.models import files
from cyberbox.routes.common import User, get_current_user, get_db

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
    file: UploadFile = File(...),
):
    # TODO save file to filesystem
    values = dict(
        uid=uuid4(), owner=user.username, filename=file.filename, content_type=file.content_type
    )
    await db.execute(files.insert().values(values))
    return values

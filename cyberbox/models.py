from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TokenModel(BaseModel):
    access_token: str
    token_type: str


class UserModel(BaseModel):
    uid: UUID
    username: str
    disabled: bool = False
    created: datetime
    is_admin: bool


class FileModel(BaseModel):
    uid: UUID
    owner: str
    filename: str
    content_type: str
    created: datetime


class LinkModel(BaseModel):
    uid: UUID
    link: str
    is_onetime: bool
    created: datetime
    visited_count: int
    valid_until: datetime = None

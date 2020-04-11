from datetime import datetime
from typing import Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel


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


DataT = TypeVar("DataT")


class Page(GenericModel, Generic[DataT]):
    items: List[DataT]
    total: int
    pages: int
    has_next: bool
    has_previous: bool
    next_page_number: Optional[bool]
    previous_page_number: Optional[bool]


class FilterParams(BaseModel):
    page: int = Field(..., ge=1)
    limit: int = Field(..., ge=1)

    def offset(self) -> int:
        return (self.page - 1) * self.limit

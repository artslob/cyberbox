from fastapi import APIRouter
from pydantic import BaseModel

from cyberbox import __version__

router = APIRouter()


class PingModel(BaseModel):
    answer: str = "pong"
    version: str = __version__


@router.get("/ping/", response_model=PingModel)
async def pong():
    return PingModel()

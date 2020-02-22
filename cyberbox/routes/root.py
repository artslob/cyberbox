from fastapi import APIRouter
from starlette.requests import Request

from cyberbox.templates import templates

router = APIRouter()


@router.get("/")
async def root(request: Request):
    return templates.TemplateResponse("root.html", dict(request=request))

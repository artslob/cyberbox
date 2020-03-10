from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import HTMLResponse

from cyberbox.templates import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("root.html", dict(request=request))

from fastapi import APIRouter

router = APIRouter()


@router.get("/login")
async def login():
    return "todo login"


@router.get("/logout")
async def login():
    return "todo logout"


@router.get("/profile")
async def profile():
    return "todo profile page"

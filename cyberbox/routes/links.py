from fastapi import APIRouter

router = APIRouter()


@router.post("/")
async def create_link():
    pass


@router.get("/")
async def download_file_by_link():
    pass


# TODO download by one time link


@router.delete("/")
async def delete_link():
    pass

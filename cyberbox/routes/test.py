from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()


class Item(BaseModel):
    name: str
    price: float
    is_offer: bool


@router.post("/items/{item_id}")
async def get_item(item_id: int, item: Item = None, q: str = Query(None)):
    if item:
        print(item.name)
    return dict(item_id=item_id, q=q, item=item)

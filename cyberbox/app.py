from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float
    is_offer: bool


@app.get("/")
async def root():
    return dict(a=1)


@app.post("/items/{item_id}")
async def get_item(item_id: int, item: Item = None, q: str = Query(None)):
    if item:
        print(item.name)
    return dict(item_id=item_id, q=q, item=item)

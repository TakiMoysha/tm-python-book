import os

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}


@app.get("/meta")
async def meta():
    return {"meta": os.getenv("META") or "not_set"}

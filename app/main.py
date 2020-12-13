from typing import List

from fastapi import FastAPI
from pydantic import BaseModel
from tree import Tree

tree = Tree()
app = FastAPI()


class Dim(BaseModel):
    key: str
    val: str


class Metrics(BaseModel):
    key: str
    val: int


class Item(BaseModel):
    dim: List[Dim] = None
    metrics: List[Metrics] = None


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/v1/insert/")
def inset(item: Item):
    return tree.insert_data(item.dict())


@app.get("/v1/query/{key}/{value}")
def query(key: str, value: str):
    return tree.fetch_data(key, value)
    return {"Hello": "World"}


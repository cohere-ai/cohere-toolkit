import json

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Body(BaseModel):
    payload: str


@app.post("/")
def webhook(body: Body):
    req = json.loads(body)
    print(req)
    return {"status": "success"}, 200


@app.get("/")
def hello():
    return {"status": "success"}, 200

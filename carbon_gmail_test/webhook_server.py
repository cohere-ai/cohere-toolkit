import json
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class AdditionalInformation(BaseModel):
    is_resync: bool = False
    request_id: Optional[str]

class Obj(BaseModel):
    object_type: str
    object_id: str
    additional_information: AdditionalInformation

class WebhookPayload(BaseModel):
    webhook_type: str
    obj: Obj
    customer_id: str
    timestamp: str

class Body(BaseModel):
    payload: str



@app.post("/")
def webhook(body: Body):
    req = json.loads(body.payload)
    print(req)
    try:
        payload = WebhookPayload(**req)
        if payload.webhook_type == "FILE_READY" and not payload.obj.additional_information.is_resync:
            print("Processing FILE_READY event")

    except Exception as e:
        print(str(e))
        return {"status": "failed to parse"}, 500
    return {"status": "success"}, 200


@app.get("/")
def hello():
    return {"status": "success"}, 200

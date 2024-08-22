import json
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

from carbon_gmail_test.utils import index_on_compass, init_compass, list_email_by_ids

load_dotenv()
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
        if (
            payload.webhook_type == "FILE_READY"
            and not payload.obj.additional_information.is_resync
        ):
            print("Processing FILE_READY event")
            customer_id = payload.customer_id
            file_id = payload.obj.object_id
            emails, _errs = list_email_by_ids([int(file_id)])
            statuses = index_on_compass(init_compass(), customer_id, emails)
            print(statuses)

    except Exception as e:
        print(str(e))
        return {"status": "failed to parse"}, 500
    return {"status": "success"}, 200


@app.get("/")
def hello():
    return {"status": "success"}, 200

from fastapi import APIRouter
from starlette.requests import Request

from backend.schemas.auth import Login

router = APIRouter()


@router.get("/session")
def get_session(request: Request):
    return request.session

@router.post("/login")
async def login(request: Request, login: Login):
    request.session["user"] = {"id": "abcd"}

    return login

@router.post("/auth")
async def auth(request: Request):
    import pdb 
    pdb.set_trace()

    return {}

@router.get("/logout")
async def logout(request: Request):
    request.session.pop("user", None)

    return {}

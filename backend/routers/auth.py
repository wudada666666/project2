from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from deps import get_current_user
from services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


class AuthBody(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=6, max_length=64)
    captcha_id: str
    captcha_answer: str


@router.get("/captcha")
def captcha():
    return auth_service.generate_captcha()


@router.post("/register")
def register(body: AuthBody):
    try:
        return auth_service.register(body.username, body.password, body.captcha_id, body.captcha_answer)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
def login(body: AuthBody):
    try:
        return auth_service.login(body.username, body.password, body.captcha_id, body.captcha_answer)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me")
def me(user: dict = Depends(get_current_user)):
    return user

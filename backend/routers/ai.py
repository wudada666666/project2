from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from deps import get_current_user
from services import ai_service, auth_service

router = APIRouter(prefix="/api/ai", tags=["ai"])


class SentenceCheck(BaseModel):
    word: str
    sentence: str


@router.get("/free-uses")
def get_free_uses(user: dict = Depends(get_current_user)):
    used = auth_service.get_free_ai_uses(user["id"])
    return {"used": used, "limit": auth_service.FREE_AI_LIMIT, "remaining": max(0, auth_service.FREE_AI_LIMIT - used)}


@router.post("/check-sentence")
def check_sentence(
    body: SentenceCheck,
    user: dict = Depends(get_current_user),
    x_deepseek_key: str | None = Header(default=None, alias="X-DeepSeek-Key"),
):
    used = auth_service.get_free_ai_uses(user["id"])
    if used < auth_service.FREE_AI_LIMIT:
        api_key = auth_service.BUILTIN_DEEPSEEK_KEY
        auth_service.increment_free_ai_uses(user["id"])
    elif x_deepseek_key:
        api_key = x_deepseek_key
    else:
        remaining = auth_service.FREE_AI_LIMIT - used
        raise HTTPException(
            status_code=400,
            detail=f"免费额度已用完（剩余 {max(remaining, 0)} 次），请在下方填写自己的 DeepSeek API Key",
        )
    try:
        return ai_service.check_sentence(body.word, body.sentence, api_key)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

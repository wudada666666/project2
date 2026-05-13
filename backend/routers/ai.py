from fastapi import APIRouter, Query
from pydantic import BaseModel
from services import ai_service

router = APIRouter(prefix="/api/ai", tags=["ai"])


class SentenceCheck(BaseModel):
    word: str
    sentence: str


@router.post("/check-sentence")
def check_sentence(body: SentenceCheck):
    return ai_service.check_sentence(body.word, body.sentence)

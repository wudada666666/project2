from fastapi import APIRouter, Depends, Query
from deps import get_current_user
from services import word_service

router = APIRouter(prefix="/api/words", tags=["words"])


@router.get("")
def list_words(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user: dict = Depends(get_current_user),
):
    return word_service.get_word_list(page, size)


@router.get("/search")
def search(
    q: str = Query(..., min_length=1),
    limit: int = Query(50, le=200),
    user: dict = Depends(get_current_user),
):
    return word_service.search_words(q, limit)


@router.get("/random")
def random_words(
    count: int = Query(20, ge=1, le=200),
    user: dict = Depends(get_current_user),
):
    return word_service.get_random_unmastered(count, user["id"])


@router.get("/review-due")
def review_due(user: dict = Depends(get_current_user)):
    return word_service.get_due_review(user["id"])


@router.get("/{word_id}")
def get_word(word_id: int, user: dict = Depends(get_current_user)):
    w = word_service.get_word_by_id(word_id)
    return w or {"error": "not found"}


@router.post("/spell-check")
def spell_check(word_id: int, answer: str, user: dict = Depends(get_current_user)):
    w = word_service.get_word_by_id(word_id)
    if not w:
        return {"correct": False, "message": "单词不存在"}
    correct = answer.strip().lower() == w["english"].strip().lower()
    if correct:
        return {"correct": True, "message": "拼写正确！"}
    similar = sum(1 for a, b in zip(answer.strip(), w["english"]) if a == b)
    return {
        "correct": False,
        "message": f"拼写不正确，相似度 {similar}/{len(w['english'])}，正确答案是 {w['english']}",
    }

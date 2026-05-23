from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from deps import get_current_user
from services import progress_service, word_service
from schemas import ProgressMark, FavoriteMark

router = APIRouter(prefix="/api/progress", tags=["progress"])


class SessionData(BaseModel):
    total: int
    correct: int
    wrong: int
    duration: int


class ConfirmReviewReq(BaseModel):
    word_id: int


@router.post("/mark")
def mark(m: ProgressMark, user: dict = Depends(get_current_user)):
    return progress_service.mark_progress(user["id"], m.word_id, m.status)


@router.get("/stats")
def stats(user: dict = Depends(get_current_user)):
    return progress_service.get_progress_stats(user["id"])


@router.get("/wrong")
def wrong_words(user: dict = Depends(get_current_user)):
    ids = progress_service.get_wrong_words(user["id"])
    return [w for wid in ids if (w := word_service.get_word_by_id(wid))]


@router.post("/favorites")
def toggle_favorite(m: FavoriteMark, user: dict = Depends(get_current_user)):
    return progress_service.manage_favorites(user["id"], m.word_id, m.action)


@router.get("/favorites")
def favorites(user: dict = Depends(get_current_user)):
    return [w for wid in progress_service.get_favorites(user["id"]) if (w := word_service.get_word_by_id(wid))]


@router.post("/session")
def save_session(s: SessionData, user: dict = Depends(get_current_user)):
    return progress_service.save_session(user["id"], s.total, s.correct, s.wrong, s.duration)


@router.get("/session/last")
def last_session(user: dict = Depends(get_current_user)):
    return progress_service.get_last_session(user["id"])


@router.get("/session/total")
def total_stats(user: dict = Depends(get_current_user)):
    return progress_service.get_total_stats(user["id"])


@router.get("/pending-review")
def pending_review(user: dict = Depends(get_current_user)):
    return progress_service.get_pending_review_words(user["id"])


@router.post("/confirm-review")
def confirm_review(req: ConfirmReviewReq, user: dict = Depends(get_current_user)):
    return progress_service.confirm_review(user["id"], req.word_id)

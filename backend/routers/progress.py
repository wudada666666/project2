from fastapi import APIRouter
from pydantic import BaseModel
from services import progress_service, word_service
from schemas import ProgressMark, FavoriteMark

router = APIRouter(prefix="/api/progress", tags=["progress"])


class SessionData(BaseModel):
    total: int
    correct: int
    wrong: int
    duration: int


@router.post("/mark")
def mark(m: ProgressMark):
    return progress_service.mark_progress(m.word_id, m.status)


@router.get("/stats")
def stats():
    return progress_service.get_progress_stats()


@router.get("/wrong")
def wrong_words():
    ids = progress_service.get_wrong_words()
    return [w for wid in ids if (w := word_service.get_word_by_id(wid))]


@router.post("/favorites")
def toggle_favorite(m: FavoriteMark):
    return progress_service.manage_favorites(m.word_id, m.action)


@router.get("/favorites")
def favorites():
    return [w for wid in progress_service.get_favorites() if (w := word_service.get_word_by_id(wid))]


@router.post("/session")
def save_session(s: SessionData):
    return progress_service.save_session(s.total, s.correct, s.wrong, s.duration)


@router.get("/session/last")
def last_session():
    return progress_service.get_last_session()


@router.get("/session/total")
def total_stats():
    return progress_service.get_total_stats()


@router.get("/pending-review")
def pending_review():
    return progress_service.get_pending_review_words()


class ConfirmReviewReq(BaseModel):
    word_id: int


@router.post("/confirm-review")
def confirm_review(req: ConfirmReviewReq):
    return progress_service.confirm_review(req.word_id)

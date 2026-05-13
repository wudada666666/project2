import json
from pathlib import Path
from database import get_connection

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
SESSION_FILE = DATA_DIR / "last_session.json"


def mark_progress(word_id: int, status: int):
    """status: 1=已掌握(斩) 2=待复习(认识) 3=不认识"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM word_progress WHERE word_id = %s", (word_id,))
            row = cur.fetchone()
            if row:
                cur.execute("""
                    UPDATE word_progress SET
                        status = %s,
                        review_count = review_count + 1,
                        last_review_at = NOW()
                    WHERE word_id = %s
                """, (status, word_id))
            else:
                cur.execute("""
                    INSERT INTO word_progress (word_id, status, review_count, last_review_at)
                    VALUES (%s, %s, 1, NOW())
                """, (word_id, status))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}


def get_progress_stats() -> dict:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS c FROM cet6zx")
            total = cur.fetchone()["c"]
            cur.execute("SELECT status, COUNT(*) AS cnt FROM word_progress GROUP BY status")
            rows = {r["status"]: r["cnt"] for r in cur.fetchall()}
            mastered, unclear, unknown = rows.get(1, 0), rows.get(2, 0), rows.get(3, 0)
        return {"total": total, "mastered": mastered, "unclear": unclear, "unknown": unknown, "unmarked": total - mastered - unclear - unknown}
    finally:
        conn.close()


def get_wrong_words():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT word_id FROM word_progress WHERE status = 3")
            return [r["word_id"] for r in cur.fetchall()]
    finally:
        conn.close()


def manage_favorites(word_id: int, action: str):
    f = DATA_DIR / "favorites.json"
    favs = json.loads(f.read_text()) if f.exists() else {}
    if action == "remove":
        favs.pop(str(word_id), None)
    else:
        favs[str(word_id)] = True
    f.write_text(json.dumps(favs))
    return {"ok": True}


def get_favorites():
    f = DATA_DIR / "favorites.json"
    if not f.exists():
        return []
    return [int(k) for k in json.loads(f.read_text())]


def save_session(total: int, correct: int, wrong: int, duration: int):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO study_sessions (started_at, ended_at, words_total, words_correct, words_wrong, duration_sec)
                VALUES (NOW() - INTERVAL %s SECOND, NOW(), %s, %s, %s, %s)
            """, (duration, total, correct, wrong, duration))
            sid = cur.lastrowid
        conn.commit()
        data = {"total": total, "correct": correct, "wrong": wrong, "duration": duration, "accuracy": round(correct / total * 100, 1) if total else 0}
        SESSION_FILE.write_text(json.dumps(data))
        return {"ok": True, "session_id": sid}
    finally:
        conn.close()


def get_last_session() -> dict:
    if SESSION_FILE.exists():
        return json.loads(SESSION_FILE.read_text())
    return {"total": 0, "correct": 0, "wrong": 0, "duration": 0, "accuracy": 0}


def get_pending_review_words():
    """Get words marked as status=2 (认识, pending review confirmation)."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT t.id, t.english, t.sent, t.chinese, p.review_count, p.last_review_at
                FROM cet6zx t
                JOIN word_progress p ON t.id = p.word_id
                WHERE p.status = 2
                ORDER BY p.last_review_at ASC
            """)
            return cur.fetchall()
    finally:
        conn.close()


def confirm_review(word_id: int):
    """Upgrade a word from status=2 (pending review) to status=1 (mastered)."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE word_progress SET
                    status = 1,
                    review_count = review_count + 1,
                    last_review_at = NOW()
                WHERE word_id = %s AND status = 2
            """, (word_id,))
            if cur.rowcount == 0:
                return {"ok": False, "error": "word not found or not pending"}
        conn.commit()
        return {"ok": True}
    finally:
        conn.close()


def get_total_stats() -> dict:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS sessions, COALESCE(SUM(words_total),0) AS tw, COALESCE(SUM(words_correct),0) AS tc, COALESCE(SUM(duration_sec),0) AS ts FROM study_sessions")
            r = cur.fetchone()
            cur.execute("SELECT COUNT(*) AS cnt FROM word_progress WHERE status = 1")
            m = cur.fetchone()
        return {"sessions": r["sessions"], "total_words": int(r["tw"]), "total_correct": int(r["tc"]), "total_sec": int(r["ts"]), "mastered": m["cnt"]}
    finally:
        conn.close()

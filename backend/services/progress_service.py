from database import get_connection


def mark_progress(user_id: int, word_id: int, status: int):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM word_progress WHERE user_id = %s AND word_id = %s",
                (user_id, word_id),
            )
            row = cur.fetchone()
            if row:
                cur.execute("""
                    UPDATE word_progress SET
                        status = %s,
                        review_count = review_count + 1,
                        last_review_at = NOW()
                    WHERE user_id = %s AND word_id = %s
                """, (status, user_id, word_id))
            else:
                cur.execute("""
                    INSERT INTO word_progress (user_id, word_id, status, review_count, last_review_at)
                    VALUES (%s, %s, %s, 1, NOW())
                """, (user_id, word_id, status))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}


def get_progress_stats(user_id: int) -> dict:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS c FROM cet6zx")
            total = cur.fetchone()["c"]
            cur.execute(
                "SELECT status, COUNT(*) AS cnt FROM word_progress WHERE user_id = %s GROUP BY status",
                (user_id,),
            )
            rows = {r["status"]: r["cnt"] for r in cur.fetchall()}
            mastered, unclear, unknown = rows.get(1, 0), rows.get(2, 0), rows.get(3, 0)
        return {
            "total": total,
            "mastered": mastered,
            "unclear": unclear,
            "unknown": unknown,
            "unmarked": total - mastered - unclear - unknown,
        }
    finally:
        conn.close()


def get_wrong_words(user_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT word_id FROM word_progress WHERE user_id = %s AND status = 3",
                (user_id,),
            )
            return [r["word_id"] for r in cur.fetchall()]
    finally:
        conn.close()


def manage_favorites(user_id: int, word_id: int, action: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if action == "remove":
                cur.execute(
                    "DELETE FROM user_favorites WHERE user_id = %s AND word_id = %s",
                    (user_id, word_id),
                )
            else:
                cur.execute(
                    "INSERT IGNORE INTO user_favorites (user_id, word_id) VALUES (%s, %s)",
                    (user_id, word_id),
                )
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}


def get_favorites(user_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT word_id FROM user_favorites WHERE user_id = %s ORDER BY created_at DESC",
                (user_id,),
            )
            return [r["word_id"] for r in cur.fetchall()]
    finally:
        conn.close()


def save_session(user_id: int, total: int, correct: int, wrong: int, duration: int):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO study_sessions (user_id, started_at, ended_at, words_total, words_correct, words_wrong, duration_sec)
                VALUES (%s, NOW() - INTERVAL %s SECOND, NOW(), %s, %s, %s, %s)
            """, (user_id, duration, total, correct, wrong, duration))
            sid = cur.lastrowid
        conn.commit()
        return {
            "ok": True,
            "session_id": sid,
            "total": total,
            "correct": correct,
            "wrong": wrong,
            "duration": duration,
            "accuracy": round(correct / total * 100, 1) if total else 0,
        }
    finally:
        conn.close()


def get_last_session(user_id: int) -> dict:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT words_total AS total, words_correct AS correct, words_wrong AS wrong,
                       duration_sec AS duration
                FROM study_sessions
                WHERE user_id = %s
                ORDER BY id DESC
                LIMIT 1
            """, (user_id,))
            row = cur.fetchone()
        if not row:
            return {"total": 0, "correct": 0, "wrong": 0, "duration": 0, "accuracy": 0}
        total = int(row["total"] or 0)
        correct = int(row["correct"] or 0)
        return {
            "total": total,
            "correct": correct,
            "wrong": int(row["wrong"] or 0),
            "duration": int(row["duration"] or 0),
            "accuracy": round(correct / total * 100, 1) if total else 0,
        }
    finally:
        conn.close()


def get_pending_review_words(user_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT t.id, t.english, t.sent, t.chinese, p.review_count, p.last_review_at
                FROM cet6zx t
                JOIN word_progress p ON t.id = p.word_id
                WHERE p.user_id = %s AND p.status = 2
                ORDER BY p.last_review_at ASC
            """, (user_id,))
            return cur.fetchall()
    finally:
        conn.close()


def confirm_review(user_id: int, word_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE word_progress SET
                    status = 1,
                    review_count = review_count + 1,
                    last_review_at = NOW()
                WHERE user_id = %s AND word_id = %s AND status = 2
            """, (user_id, word_id))
            if cur.rowcount == 0:
                return {"ok": False, "error": "word not found or not pending"}
        conn.commit()
        return {"ok": True}
    finally:
        conn.close()


def get_total_stats(user_id: int) -> dict:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) AS sessions, COALESCE(SUM(words_total),0) AS tw,
                       COALESCE(SUM(words_correct),0) AS tc, COALESCE(SUM(duration_sec),0) AS ts
                FROM study_sessions WHERE user_id = %s
            """, (user_id,))
            r = cur.fetchone()
            cur.execute(
                "SELECT COUNT(*) AS cnt FROM word_progress WHERE user_id = %s AND status = 1",
                (user_id,),
            )
            m = cur.fetchone()
        return {
            "sessions": r["sessions"],
            "total_words": int(r["tw"]),
            "total_correct": int(r["tc"]),
            "total_sec": int(r["ts"]),
            "mastered": m["cnt"],
        }
    finally:
        conn.close()

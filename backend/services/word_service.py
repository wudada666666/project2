from database import get_connection

TABLE = "cet6zx"


def get_word_list(page: int = 1, size: int = 20):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) AS c FROM `{TABLE}`")
            total = cur.fetchone()["c"]
            offset = (page - 1) * size
            cur.execute(f"SELECT id, english, sent, chinese FROM `{TABLE}` ORDER BY id LIMIT %s OFFSET %s", (size, offset))
            items = cur.fetchall()
            return {"total": total, "page": page, "size": size, "items": items}
    finally:
        conn.close()


def search_words(q: str, limit: int = 50):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT id, english, sent, chinese FROM `{TABLE}` WHERE english LIKE %s OR chinese LIKE %s LIMIT %s", (f"%{q}%", f"%{q}%", limit))
            return cur.fetchall()
    finally:
        conn.close()


def get_word_by_id(word_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT id, english, sent, chinese FROM `{TABLE}` WHERE id = %s", (word_id,))
            return cur.fetchone()
    finally:
        conn.close()


def get_random_unmastered(count: int = 20):
    """Random words that aren't mastered or pending review (status != 1 and != 2)."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Words excluded from random study: mastered (1) + pending review (2)
            excluded_set = set()
            cur.execute("SELECT word_id FROM word_progress WHERE status IN (1, 2)")
            excluded_set.update(r["word_id"] for r in cur.fetchall())

            # Words with status=3 (不认识) get higher weight
            cur.execute("SELECT word_id FROM word_progress WHERE status = 3")
            unknown_ids = {r["word_id"] for r in cur.fetchall()}

            result = []
            # Phase 1: unknown words (status=3) priority
            if unknown_ids:
                placeholders = ','.join(['%s'] * len(unknown_ids))
                cur.execute(f"SELECT id, english, sent, chinese FROM `{TABLE}` WHERE id IN ({placeholders}) ORDER BY RAND()", tuple(unknown_ids))
                result.extend(cur.fetchall())

            # Phase 2: unmarked words (no progress record or status=0)
            if excluded_set:
                placeholders = ','.join(['%s'] * len(excluded_set))
                cur.execute(f"""
                    SELECT id, english, sent, chinese FROM `{TABLE}`
                    WHERE id NOT IN ({placeholders})
                      AND id NOT IN (SELECT word_id FROM word_progress WHERE status = 3)
                    ORDER BY RAND() LIMIT %s
                """, tuple(excluded_set) + (count * 2,))
            else:
                cur.execute(f"""
                    SELECT id, english, sent, chinese FROM `{TABLE}`
                    WHERE id NOT IN (SELECT word_id FROM word_progress WHERE status = 3)
                    ORDER BY RAND() LIMIT %s
                """, (count * 2,))
            result.extend(cur.fetchall())

            return result[:count]
    finally:
        conn.close()


def get_due_review():
    """Get words with progress records for review, ordered by last review time."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT t.id, t.english, t.sent, t.chinese, p.review_count, p.status
                FROM cet6zx t
                JOIN word_progress p ON t.id = p.word_id
                WHERE p.status IN (1, 2)
                ORDER BY p.last_review_at ASC
                LIMIT 100
            """)
            return cur.fetchall()
    finally:
        conn.close()

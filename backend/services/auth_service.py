import os
import random
import re
import time
import uuid

import bcrypt
import jwt
from database import get_connection

JWT_SECRET = os.environ.get("JWT_SECRET", "cet6zx-change-me-in-production")
JWT_ALG = "HS256"
JWT_EXPIRE_SEC = 60 * 60 * 24 * 7

_captcha_store: dict[str, tuple[int, float]] = {}


def _cleanup_captcha():
    now = time.time()
    expired = [k for k, (_, exp) in _captcha_store.items() if exp < now]
    for k in expired:
        _captcha_store.pop(k, None)


def generate_captcha() -> dict:
    _cleanup_captcha()
    a = random.randint(1, 9)
    b = random.randint(1, 9)
    op = random.choice(["+", "-", "×"])
    if op == "+":
        answer = a + b
    elif op == "-":
        if a < b:
            a, b = b, a
        answer = a - b
    else:
        answer = a * b
    captcha_id = str(uuid.uuid4())
    _captcha_store[captcha_id] = (answer, time.time() + 300)
    return {"captcha_id": captcha_id, "question": f"{a} {op} {b} = ?"}


def verify_captcha(captcha_id: str, answer: str) -> bool:
    _cleanup_captcha()
    item = _captcha_store.pop(captcha_id, None)
    if not item:
        return False
    expected, expires = item
    if time.time() > expires:
        return False
    try:
        return int(str(answer).strip()) == expected
    except ValueError:
        return False


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def _validate_username(username: str):
    if not re.fullmatch(r"[A-Za-z0-9_]{3,20}", username):
        raise ValueError("用户名需为 3-20 位字母、数字或下划线")


def _validate_password(password: str):
    if len(password) < 6:
        raise ValueError("密码至少 6 位")


def register(username: str, password: str, captcha_id: str, captcha_answer: str) -> dict:
    _validate_username(username)
    _validate_password(password)
    if not verify_captcha(captcha_id, captcha_answer):
        raise ValueError("验证码错误或已过期")

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cur.fetchone():
                raise ValueError("用户名已存在")
            cur.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, _hash_password(password)),
            )
            user_id = cur.lastrowid
        conn.commit()
    finally:
        conn.close()
    return {"token": _create_token(user_id, username), "username": username}


def login(username: str, password: str, captcha_id: str, captcha_answer: str) -> dict:
    if not verify_captcha(captcha_id, captcha_answer):
        raise ValueError("验证码错误或已过期")

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, username, password_hash FROM users WHERE username = %s", (username,))
            row = cur.fetchone()
    finally:
        conn.close()

    if not row or not _check_password(password, row["password_hash"]):
        raise ValueError("用户名或密码错误")

    return {"token": _create_token(row["id"], row["username"]), "username": row["username"]}


def _create_token(user_id: int, username: str) -> str:
    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": int(time.time()) + JWT_EXPIRE_SEC,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def get_user_from_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        return {"id": int(payload["sub"]), "username": payload["username"]}
    except jwt.PyJWTError:
        return None


FREE_AI_LIMIT = 10
BUILTIN_DEEPSEEK_KEY = "sk-eaea1591c784440b97e2301ca87a3439"


def get_free_ai_uses(user_id: int) -> int:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT free_ai_uses FROM users WHERE id = %s", (user_id,))
            row = cur.fetchone()
            return row["free_ai_uses"] if row else 0
    finally:
        conn.close()


def increment_free_ai_uses(user_id: int) -> int:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET free_ai_uses = free_ai_uses + 1 WHERE id = %s",
                (user_id,),
            )
            conn.commit()
            cur.execute("SELECT free_ai_uses FROM users WHERE id = %s", (user_id,))
            return cur.fetchone()["free_ai_uses"]
    finally:
        conn.close()

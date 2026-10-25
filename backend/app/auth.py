import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .database import db, q1

SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me-please-use-a-long-random-string")
ALGO = "HS256"
TOKEN_HOURS = 24 * 7
bearer = HTTPBearer(auto_error=False)


def hash_password(password, salt=None):
    salt = salt or secrets.token_hex(8)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()
    return f"{salt}${digest}"


def verify_password(password, stored):
    try:
        salt, _ = stored.split("$", 1)
    except ValueError:
        return False
    return hmac.compare_digest(hash_password(password, salt), stored)


def make_token(user_id):
    exp = datetime.now(timezone.utc) + timedelta(hours=TOKEN_HOURS)
    return jwt.encode({"sub": str(user_id), "exp": exp}, SECRET, algorithm=ALGO)


def current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    if not creds:
        raise HTTPException(401, "Not authenticated")
    try:
        data = jwt.decode(creds.credentials, SECRET, algorithms=[ALGO])
        user_id = int(data["sub"])
    except Exception:
        raise HTTPException(401, "Invalid or expired token")
    with db() as conn:
        user = q1(conn, "SELECT id, name, email, role, home_city, travel_style FROM users WHERE id = ?", (user_id,))
    if not user:
        raise HTTPException(401, "User not found")
    return user

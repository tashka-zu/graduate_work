from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import secrets
from typing import Any

import jwt

from authentication.config import JWT_ALGORITHM, JWT_EXPIRE_MINUTES, JWT_SECRET


def hash_password(password: str) -> str:
    """
    Hash password without external native deps.

    Stored format: `pbkdf2_sha256$<iterations>$<salt_hex>$<hash_hex>`
    """
    salt = secrets.token_hex(16)
    iterations = 200_000
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations)
    return f"pbkdf2_sha256${iterations}${salt}${dk.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algo, iterations_s, salt_hex, hash_hex = password_hash.split("$", 3)
        if algo != "pbkdf2_sha256":
            return False
        iterations = int(iterations_s)
        dk = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt_hex.encode("utf-8"),
            iterations,
        )
        return hmac.compare_digest(dk.hex(), hash_hex)
    except Exception:
        return False


def create_access_token(user_id: int) -> str:
    now = datetime.now(tz=timezone.utc)
    exp = now + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    # Throws jwt exceptions on invalid tokens; caller can map to Unauthorized.
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


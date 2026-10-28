from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import os
import jwt
from fastapi import HTTPException, status
from app.core.config import settings

PBKDF2_ITERATIONS = 600_000
MIN_ACCEPTED_ITERATIONS = 100_000
MAX_ACCEPTED_ITERATIONS = 1_000_000


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        scheme, iterations, salt_hex, digest_hex = encoded.split("$")
        iterations = int(iterations)
        if scheme != "pbkdf2_sha256" or not MIN_ACCEPTED_ITERATIONS <= iterations <= MAX_ACCEPTED_ITERATIONS:
            return False
        candidate = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), iterations)
        return hmac.compare_digest(candidate.hex(), digest_hex)
    except (AttributeError, TypeError, ValueError, OverflowError):
        return False


def password_needs_rehash(encoded: str) -> bool:
    try:
        scheme, iterations, _, _ = encoded.split("$")
        return scheme != "pbkdf2_sha256" or int(iterations) < PBKDF2_ITERATIONS
    except (AttributeError, TypeError, ValueError):
        return True


def create_access_token(user_id: int) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_minutes)
    return jwt.encode({"sub": str(user_id), "exp": expires}, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> int:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

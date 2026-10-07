import base64
import hashlib
import hmac
import json
import os
import time

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User


_bearer = HTTPBearer(auto_error=False)
_secret = os.getenv("SECRET_KEY", "local-development-key-change-before-deployment").encode()


def _encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
    return f"{_encode(salt)}${_encode(digest)}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        salt_text, digest_text = encoded.split("$", 1)
        salt = base64.urlsafe_b64decode(salt_text + "=" * (-len(salt_text) % 4))
        expected = base64.urlsafe_b64decode(digest_text + "=" * (-len(digest_text) % 4))
    except (ValueError, TypeError):
        return False
    actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
    return hmac.compare_digest(actual, expected)


def create_access_token(user_id: int) -> str:
    header = _encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = _encode(json.dumps({"sub": str(user_id), "exp": int(time.time()) + 3600}).encode())
    signed = f"{header}.{payload}"
    signature = _encode(hmac.new(_secret, signed.encode(), hashlib.sha256).digest())
    return f"{signed}.{signature}"


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    unauthorized = HTTPException(
        status_code=401,
        detail="A valid bearer token is required",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized

    try:
        header, payload, signature = credentials.credentials.split(".")
        signed = f"{header}.{payload}"
        expected = _encode(hmac.new(_secret, signed.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected):
            raise unauthorized
        payload_bytes = base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4))
        claims = json.loads(payload_bytes)
        if int(claims["exp"]) <= int(time.time()):
            raise unauthorized
        user_id = int(claims["sub"])
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        raise unauthorized from None

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise unauthorized
    return user

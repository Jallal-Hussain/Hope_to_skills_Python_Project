import bcrypt
import hashlib
import os
import secrets
from datetime import datetime, timedelta, UTC
from typing import Optional

from jose import JWTError, jwt

from src.db import SessionLocal
from src.models import RevokedToken

SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY environment variable is not set.")
if len(SECRET_KEY.encode("utf-8")) < 32:
    raise RuntimeError("JWT_SECRET_KEY must be at least 32 bytes long for secure signing.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
PASSWORD_RESET_TOKEN_TTL_MINUTES = 15


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def hash_token(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def generate_reset_token() -> str:
    return secrets.token_urlsafe(32)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": datetime.now(UTC), "nbf": datetime.now(UTC)})
    if "jti" not in to_encode:
        to_encode["jti"] = secrets.token_urlsafe(32)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if not payload.get("jti"):
            return None
        db = SessionLocal()
        try:
            revoked = db.query(RevokedToken).filter_by(jti=payload["jti"]).first()
            if revoked is not None and revoked.expires_at > datetime.now(UTC):
                return None
        finally:
            db.close()
        return payload
    except JWTError:
        return None


def revoke_token(token: str, user_id: int):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return False

    jti = payload.get("jti")
    exp = payload.get("exp")
    if not jti or not exp:
        return False

    expires_at = datetime.fromtimestamp(exp, tz=UTC)
    db = SessionLocal()
    try:
        existing = db.query(RevokedToken).filter_by(jti=jti).first()
        if existing is None:
            db.add(RevokedToken(jti=jti, user_id=user_id, expires_at=expires_at))
            db.commit()
            return True
        return True
    finally:
        db.close()
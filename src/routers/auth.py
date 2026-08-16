import os
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta, UTC

from fastapi import APIRouter, HTTPException, status, Depends, Response, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.db import SessionLocal
from src.models import User, Document, Conversation, ChatMessage, PasswordResetToken
from src.utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    generate_reset_token,
    hash_token,
    revoke_token,
    PASSWORD_RESET_TOKEN_TTL_MINUTES,
)
from src.config import APP_ENV
from loguru import logger

router = APIRouter()


class RateLimiter:
    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds
        self._requests = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        requests = self._requests[key]
        while requests and now - requests[0] >= self.window_seconds:
            requests.popleft()
        if len(requests) >= self.limit:
            return False
        requests.append(now)
        return True


login_rate_limiter = RateLimiter(limit=5, window_seconds=60)
register_rate_limiter = RateLimiter(limit=5, window_seconds=3600)
password_reset_rate_limiter = RateLimiter(limit=3, window_seconds=3600)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UserCreate(BaseModel):
    username: str
    password: str

    def validate_password_length(self):
        """Ensure password doesn't exceed 72 bytes (bcrypt limit)"""
        if len(self.password.encode('utf-8')) > 72:
            raise ValueError("Password must not exceed 72 bytes")


class UserLogin(BaseModel):
    username: str
    password: str


@router.post("/register", status_code=201)
def register(user: UserCreate, request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    if not register_rate_limiter.allow(client_ip):
        raise HTTPException(status_code=429, detail="Too many registration attempts. Please try again later.")
    try:
        user.validate_password_length()
    except ValueError as e:
        logger.error(f"Register error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    if db.query(User).filter_by(username=user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed = hash_password(user.password)
    db_user = User(username=user.username, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User registered successfully"}


@router.post("/login")
def login(user: UserLogin, request: Request, response: Response, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    if not login_rate_limiter.allow(client_ip):
        raise HTTPException(status_code=429, detail="Too many login attempts. Please try again later.")
    db_user = db.query(User).filter_by(username=user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token({"sub": db_user.username, "user_id": db_user.id})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=APP_ENV == "production",
        samesite="lax",
        path="/",
        max_age=60 * 60,
    )
    return {"message": "Login successful"}


class PasswordResetRequest(BaseModel):
    username: str


class PasswordResetConfirm(BaseModel):
    username: str
    token: str
    new_password: str

    def validate_password_length(self):
        if len(self.new_password.encode('utf-8')) > 72:
            raise ValueError("Password must not exceed 72 bytes")


@router.post("/password-reset")
def password_reset(payload: PasswordResetRequest, request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    if not password_reset_rate_limiter.allow(client_ip):
        raise HTTPException(status_code=429, detail="Too many password reset attempts. Please try again later.")

    user = db.query(User).filter_by(username=payload.username).first()
    if not user:
        return {"message": "If the username exists, a reset link has been sent."}

    token = generate_reset_token()
    token_hash = hash_token(token)
    expires_at = datetime.now(UTC) + timedelta(minutes=PASSWORD_RESET_TOKEN_TTL_MINUTES)

    existing_tokens = db.query(PasswordResetToken).filter_by(user_id=user.id).all()
    for existing in existing_tokens:
        db.delete(existing)

    reset_token = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(reset_token)
    db.commit()

    logger.info(f"Password reset token created for user {user.id} from {client_ip}")
    return {
        "message": "If the username exists, a reset link has been sent.",
        "expires_in_minutes": PASSWORD_RESET_TOKEN_TTL_MINUTES,
    }


@router.post("/password-reset/confirm")
def confirm_password_reset(payload: PasswordResetConfirm, request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    if not password_reset_rate_limiter.allow(client_ip):
        raise HTTPException(status_code=429, detail="Too many password reset attempts. Please try again later.")

    try:
        payload.validate_password_length()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    user = db.query(User).filter_by(username=payload.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid reset request.")

    token_hash = hash_token(payload.token)
    reset_token = db.query(PasswordResetToken).filter_by(user_id=user.id, token_hash=token_hash).first()
    if not reset_token:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")

    if reset_token.used_at is not None or reset_token.expires_at < datetime.now(UTC):
        db.delete(reset_token)
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")

    user.hashed_password = hash_password(payload.new_password)
    reset_token.used_at = datetime.now(UTC)
    db.commit()
    return {"message": "Password reset successfully."}


@router.post("/otp")
def otp(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    if not password_reset_rate_limiter.allow(client_ip):
        raise HTTPException(status_code=429, detail="Too many OTP attempts. Please try again later.")
    raise HTTPException(status_code=501, detail="OTP authentication is not currently enabled.")

def get_current_user_from_cookie(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    payload = decode_access_token(token)
    if not payload or "user_id" not in payload:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    user = db.query(User).filter_by(id=payload["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/session")
def get_session_status(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")

    payload = decode_access_token(token)
    if not payload or "user_id" not in payload:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    user = db.query(User).filter_by(id=payload["user_id"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return {"authenticated": True, "user_id": user.id, "username": user.username}


@router.post("/logout")
def logout(response: Response, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_from_cookie)):
    token = request.cookies.get("access_token")
    if token:
        revoke_token(token, current_user.id)
    response.delete_cookie(key="access_token", path="/")
    return {"message": "Logged out successfully"}

@router.delete("/delete-account")
def delete_account(db: Session = Depends(get_db), current_user: User = Depends(get_current_user_from_cookie)):
    doc_rows = db.query(Document).filter_by(user_id=current_user.id).all()
    for doc in doc_rows:
        if doc.file_path and os.path.exists(doc.file_path):
            try:
                os.remove(doc.file_path)
            except OSError:
                pass
        db.delete(doc)

    conv_rows = db.query(Conversation).filter_by(user_id=current_user.id).all()
    for conv in conv_rows:
        msg_rows = db.query(ChatMessage).filter_by(conversation_id=conv.id).all()
        for msg in msg_rows:
            db.delete(msg)
        db.delete(conv)

    db.delete(current_user)
    db.commit()
    return {"message": "Account and personal data deleted successfully"} 
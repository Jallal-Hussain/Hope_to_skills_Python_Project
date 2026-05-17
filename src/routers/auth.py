from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from src.db import SessionLocal
from src.models import User
from src.utils.auth import hash_password, verify_password, create_access_token
from pydantic import BaseModel
from loguru import logger

router = APIRouter()

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
def register(user: UserCreate, db: Session = Depends(get_db)):
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
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter_by(username=user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token({"sub": db_user.username, "user_id": db_user.id})
    return {"access_token": token, "token_type": "bearer"} 
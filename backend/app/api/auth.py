from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.core.security import hash_password, password_needs_rehash, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(func.lower(User.email) == str(data.email).lower()).first()
    if existing:
        raise HTTPException(status_code=409, detail="Un compte existe déjà avec cette adresse e-mail.")
    user = User(email=data.email, name=data.name, password_hash=hash_password(data.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Un compte existe déjà avec cette adresse e-mail.")
    db.refresh(user)
    return {"access_token": create_access_token(user.id), "token_type": "bearer"}


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(func.lower(User.email) == str(data.email).lower()).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Adresse e-mail ou mot de passe incorrect.")
    if password_needs_rehash(user.password_hash):
        user.password_hash = hash_password(data.password)
        db.commit()
    return {"access_token": create_access_token(user.id), "token_type": "bearer"}

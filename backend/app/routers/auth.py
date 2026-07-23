"""
Marrakech Companion - Auth Router
FR-001: نظام المصادقة (ضيف، بريد، Google)
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.core.database import get_db
from app.core.security import create_access_token, verify_password, get_password_hash
from app.models import User

router = APIRouter()


# ─── Schemas ───────────────────────────────────────────
class GuestLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    is_guest: bool = True

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    country_origin: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    full_name: Optional[str] = None
    is_guest: bool = False


# ─── Guest Login (FR-001-1) ──────────────────────────────
@router.post("/guest", response_model=GuestLoginResponse)
def guest_login(db: Session = Depends(get_db)):
    """دخول ضيف فوري بدون بيانات"""
    guest_id = str(uuid.uuid4())
    guest_email = f"guest_{guest_id[:8]}@marrakech.app"
    
    user = User(
        id=guest_id,
        email=guest_email,
        full_name="ضيف / Guest",
        is_guest=True
    )
    db.add(user)
    db.commit()
    
    token = create_access_token(data={"sub": guest_id, "is_guest": True})
    return GuestLoginResponse(access_token=token, user_id=guest_id)


# ─── Register (FR-001-2) ────────────────────────────────
@router.post("/register", response_model=AuthResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """تسجيل بالبريد + كلمة مرور"""
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="هذا البريد مسجل بالفعل / Email already registered"
        )
    
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=req.email,
        full_name=req.full_name,
        phone_number=req.phone_number,
        country_origin=req.country_origin,
        hashed_password=get_password_hash(req.password),
        is_guest=False
    )
    db.add(user)
    db.commit()
    
    token = create_access_token(data={"sub": user_id, "is_guest": False})
    return AuthResponse(
        access_token=token,
        user_id=user_id,
        full_name=req.full_name
    )


# ─── Login (FR-001-2) ───────────────────────────────────
@router.post("/login", response_model=AuthResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """تسجيل دخول بالبريد + كلمة مرور"""
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="بريد أو كلمة مرور خاطئة / Invalid credentials"
        )
    
    if not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="بريد أو كلمة مرور خاطئة / Invalid credentials"
        )
    
    token = create_access_token(data={"sub": str(user.id), "is_guest": False})
    return AuthResponse(
        access_token=token,
        user_id=str(user.id),
        full_name=user.full_name
    )

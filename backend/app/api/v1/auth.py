import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.dependencies import get_db
from app.models import CollegeDomain, EmailVerificationToken, User
from app.schemas.auth import AuthResponse, LoginRequest, ProfileUpdateRequest, RegisterRequest, UserResponse, VerifyEmailRequest
from app.services.security import create_access_token, hash_password, verify_password
from app.services.email_service import send_verification_email

router = APIRouter(prefix="/auth", tags=["auth"])
bearer_scheme = HTTPBearer()


def normalized_email(value: str) -> str:
    return value.strip().lower()


def issue_verification_token(db: Session, user: User) -> str:
    raw_token = secrets.token_urlsafe(48)
    db.add(EmailVerificationToken(user_id=user.id, token_hash=hashlib.sha256(raw_token.encode()).hexdigest(), expires_at=datetime.now(UTC) + timedelta(hours=24)))
    return raw_token


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    email = normalized_email(str(payload.email))
    domain = email.rsplit("@", 1)[1]
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=409, detail="An account already exists for this email.")
    approved_domain = db.scalar(select(CollegeDomain).where(CollegeDomain.domain == domain, CollegeDomain.is_active.is_(True)))
    if not approved_domain:
        raise HTTPException(status_code=403, detail="This college email domain is not approved.")
    user = User(email=email, password_hash=hash_password(payload.password), full_name=payload.full_name.strip(), college_name=approved_domain.college_name)
    db.add(user)
    db.flush()
    verification_token = issue_verification_token(db, user)
    db.commit()
    try:
        send_verification_email(user.email, verification_token)
    except Exception as error:
        if settings.app_env == "production":
            raise HTTPException(status_code=503, detail="Verification email delivery is unavailable.") from error
    response = {"detail": "Check your college email to verify your account."}
    if settings.app_env == "development":
        response["development_verification_token"] = verification_token
    return response


@router.post("/verify-email", response_model=UserResponse)
def verify_email(payload: VerifyEmailRequest, db: Session = Depends(get_db)) -> User:
    token_hash = hashlib.sha256(payload.token.encode()).hexdigest()
    record = db.scalar(select(EmailVerificationToken).where(EmailVerificationToken.token_hash == token_hash, EmailVerificationToken.used_at.is_(None)))
    if not record or record.expires_at < datetime.now(UTC):
        raise HTTPException(status_code=400, detail="Verification token is invalid or expired.")
    user = db.get(User, record.user_id)
    if not user:
        raise HTTPException(status_code=400, detail="Verification token is invalid.")
    user.is_email_verified = True
    record.used_at = datetime.now(UTC)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    user = db.scalar(select(User).where(User.email == normalized_email(str(payload.email))))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="This account is inactive.")
    if not user.is_email_verified:
        raise HTTPException(status_code=403, detail="Verify your email before signing in.")
    return AuthResponse(access_token=create_access_token(str(user.id)), user=user)


@router.get("/me", response_model=UserResponse)
def me(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret_key, algorithms=["HS256"])
        user_id = UUID(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid authentication token.")
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid authentication token.")
    return user


@router.patch("/me", response_model=UserResponse)
def update_me(payload: ProfileUpdateRequest, credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)) -> User:
    try:
        user_id = UUID(jwt.decode(credentials.credentials, settings.jwt_secret_key, algorithms=["HS256"])["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid authentication token.")
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid authentication token.")
    user.full_name = payload.full_name.strip()
    db.commit()
    db.refresh(user)
    return user

from datetime import UTC, datetime, timedelta

import jwt
from passlib.context import CryptContext

from app.core.config import settings

password_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return password_context.verify(password, password_hash)


def create_access_token(user_id: str) -> str:
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.jwt_access_token_minutes)
    return jwt.encode({"sub": user_id, "exp": expires_at}, settings.jwt_secret_key, algorithm="HS256")

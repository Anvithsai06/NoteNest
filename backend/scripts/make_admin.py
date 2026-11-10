"""Promote an existing verified account: python scripts/make_admin.py student@college.edu"""
import sys

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.user import User

email = sys.argv[1].strip().lower() if len(sys.argv) == 2 else ""
if not email:
    raise SystemExit("Usage: python scripts/make_admin.py student@college.edu")
with SessionLocal() as db:
    user = db.scalar(select(User).where(User.email == email))
    if not user:
        raise SystemExit("User not found.")
    if not user.is_email_verified:
        raise SystemExit("User must verify their email before promotion.")
    user.is_admin = True
    user.role = "super_admin"
    db.commit()
print(f"Promoted {email} to SUPER_ADMIN.")

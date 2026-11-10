"""create authentication foundation

Revision ID: 0001_auth_foundation
Revises:
Create Date: 2026-11-07
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_auth_foundation"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("college_domains", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("domain", sa.String(255), nullable=False, unique=True), sa.Column("college_name", sa.String(180), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.create_index("ix_college_domains_domain", "college_domains", ["domain"])
    op.create_table("users", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("email", sa.String(255), nullable=False, unique=True), sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("full_name", sa.String(120), nullable=False), sa.Column("college_name", sa.String(180), nullable=False), sa.Column("is_email_verified", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_users_email", "users", ["email"])
    op.create_table("email_verification_tokens", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("token_hash", sa.String(64), nullable=False, unique=True), sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False), sa.Column("used_at", sa.DateTime(timezone=True)), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_email_verification_tokens_user_id", "email_verification_tokens", ["user_id"])


def downgrade() -> None:
    op.drop_table("email_verification_tokens")
    op.drop_table("users")
    op.drop_table("college_domains")

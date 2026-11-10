"""add reliable note deletion state

Revision ID: 0005_note_deletion_reliability
Revises: 0004_sru_domain_and_roles
"""
from alembic import op
import sqlalchemy as sa

revision = "0005_note_deletion_reliability"
down_revision = "0004_sru_domain_and_roles"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("notes", sa.Column("deletion_status", sa.String(20), nullable=False, server_default="active"))
    op.add_column("notes", sa.Column("deletion_attempts", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("notes", sa.Column("deletion_requested_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("notes", sa.Column("last_deletion_error", sa.String(200), nullable=True))
    op.create_index("ix_notes_deletion_status", "notes", ["deletion_status"])


def downgrade() -> None:
    op.drop_index("ix_notes_deletion_status", table_name="notes")
    op.drop_column("notes", "last_deletion_error")
    op.drop_column("notes", "deletion_requested_at")
    op.drop_column("notes", "deletion_attempts")
    op.drop_column("notes", "deletion_status")

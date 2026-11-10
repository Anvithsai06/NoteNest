"""create saved notes and reports

Revision ID: 0003_library_and_reports
Revises: 0002_notes
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003_library_and_reports"
down_revision = "0002_notes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("saved_notes", sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True), sa.Column("note_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("notes.id", ondelete="CASCADE"), primary_key=True), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("reports", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("note_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("notes.id", ondelete="CASCADE"), nullable=False), sa.Column("reporter_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("reason", sa.String(60), nullable=False), sa.Column("details", sa.Text()), sa.Column("status", sa.String(20), server_default="open", nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_reports_note_id", "reports", ["note_id"])
    op.create_index("ix_reports_reporter_id", "reports", ["reporter_id"])
    op.create_index("ix_reports_status", "reports", ["status"])


def downgrade() -> None:
    op.drop_table("reports")
    op.drop_table("saved_notes")

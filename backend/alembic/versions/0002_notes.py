"""create notes

Revision ID: 0002_notes
Revises: 0001_auth_foundation
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_notes"
down_revision = "0001_auth_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("notes", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("uploader_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("title", sa.String(200), nullable=False), sa.Column("description", sa.Text()), sa.Column("subject", sa.String(120), nullable=False), sa.Column("course_code", sa.String(80)), sa.Column("semester", sa.String(50)), sa.Column("college_name", sa.String(180), nullable=False), sa.Column("original_filename", sa.String(255), nullable=False), sa.Column("stored_filename", sa.String(255), nullable=False, unique=True), sa.Column("storage_path", sa.Text(), nullable=False), sa.Column("mime_type", sa.String(120), nullable=False), sa.Column("file_size_bytes", sa.BigInteger(), nullable=False), sa.Column("visibility", sa.String(20), nullable=False, server_default="public"), sa.Column("download_count", sa.Integer(), nullable=False, server_default="0"), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))
    for column in ("uploader_id", "subject", "course_code", "college_name", "visibility", "created_at"):
        op.create_index(f"ix_notes_{column}", "notes", [column])


def downgrade() -> None:
    op.drop_table("notes")

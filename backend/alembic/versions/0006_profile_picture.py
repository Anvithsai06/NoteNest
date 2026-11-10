"""add private profile picture storage reference

Revision ID: 0006_profile_picture
Revises: 0005_note_deletion_reliability
"""
from alembic import op
import sqlalchemy as sa

revision = "0006_profile_picture"
down_revision = "0005_note_deletion_reliability"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("profile_picture_storage_path", sa.String(255), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "profile_picture_storage_path")

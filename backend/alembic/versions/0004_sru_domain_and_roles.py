"""seed SR University domain and add explicit roles

Revision ID: 0004_sru_domain_and_roles
Revises: 0003_library_and_reports
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_sru_domain_and_roles"
down_revision = "0003_library_and_reports"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("role", sa.String(20), nullable=False, server_default="student"))
    op.execute("UPDATE users SET role = 'admin' WHERE is_admin = true")
    op.execute("INSERT INTO college_domains (id, domain, college_name, is_active) VALUES ('a5dbd8f4-b1f2-4d4f-8af0-35ef6af03519', 'sru.edu.in', 'SR University', true) ON CONFLICT (domain) DO UPDATE SET college_name = EXCLUDED.college_name, is_active = true")


def downgrade() -> None:
    op.execute("DELETE FROM college_domains WHERE domain = 'sru.edu.in'")
    op.drop_column("users", "role")

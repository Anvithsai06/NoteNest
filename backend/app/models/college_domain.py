import uuid

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CollegeDomain(Base):
    __tablename__ = "college_domains"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    college_name: Mapped[str] = mapped_column(String(180))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

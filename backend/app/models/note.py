import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Note(Base):
    __tablename__ = "notes"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    uploader_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    subject: Mapped[str] = mapped_column(String(120), index=True)
    course_code: Mapped[str | None] = mapped_column(String(80), index=True, nullable=True)
    semester: Mapped[str | None] = mapped_column(String(50), nullable=True)
    college_name: Mapped[str] = mapped_column(String(180), index=True)
    original_filename: Mapped[str] = mapped_column(String(255))
    stored_filename: Mapped[str] = mapped_column(String(255), unique=True)
    storage_path: Mapped[str] = mapped_column(Text)
    mime_type: Mapped[str] = mapped_column(String(120))
    file_size_bytes: Mapped[int] = mapped_column(BigInteger)
    visibility: Mapped[str] = mapped_column(String(20), default="public", index=True)
    deletion_status: Mapped[str] = mapped_column(String(20), default="active", server_default="active", index=True)
    deletion_attempts: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    deletion_requested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_deletion_error: Mapped[str | None] = mapped_column(String(200), nullable=True)
    download_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

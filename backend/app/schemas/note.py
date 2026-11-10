from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class NoteResponse(BaseModel):
    id: UUID
    title: str
    description: str | None
    subject: str
    course_code: str | None
    semester: str | None
    college_name: str
    original_filename: str
    mime_type: str
    file_size_bytes: int
    download_count: int
    deletion_status: str
    created_at: datetime
    model_config = {"from_attributes": True}


class NoteUpdate(BaseModel):
    title: str | None = Field(None, min_length=2, max_length=200)
    description: str | None = Field(None, max_length=5000)
    subject: str | None = Field(None, min_length=2, max_length=120)
    course_code: str | None = Field(None, max_length=80)
    semester: str | None = Field(None, max_length=50)

from typing import Literal
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field


class CollegeDomainRequest(BaseModel):
    domain: str = Field(min_length=3, max_length=255)
    college_name: str = Field(min_length=2, max_length=180)


class ReportStatusRequest(BaseModel):
    status: Literal["reviewed", "dismissed", "actioned"]


class DomainResponse(BaseModel):
    id: UUID
    domain: str
    college_name: str
    is_active: bool
    model_config = {"from_attributes": True}


class ReportResponse(BaseModel):
    id: UUID
    note_id: UUID
    reporter_id: UUID
    reason: str
    details: str | None
    status: str
    created_at: datetime
    model_config = {"from_attributes": True}

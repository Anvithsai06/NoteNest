from typing import Literal
from pydantic import BaseModel, Field


class ReportRequest(BaseModel):
    reason: Literal["copyright", "spam", "inappropriate", "other"]
    details: str | None = Field(None, max_length=2000)

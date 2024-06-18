from datetime import datetime, UTC
from pydantic import BaseModel, Field


class MessageProgram(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    slug: str
    reports_count: int

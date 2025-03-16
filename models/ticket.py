from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class TicketStatus(str, Enum):
    UNINITIALIZED = "uninitialized"
    PROCESSING = "processing"
    DONE = "done"


class Ticket(BaseModel):
    id: str
    question: str
    status: TicketStatus = TicketStatus.UNINITIALIZED
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    answer: Optional[str] = None
    note: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert ticket to dictionary"""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict) -> "Ticket":
        """Create ticket from dictionary"""
        return cls.model_validate(data)
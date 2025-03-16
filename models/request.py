from pydantic import BaseModel
from typing import Optional
from models.ticket import TicketStatus


class CreateTicketRequest(BaseModel):
    question: str


class CreateTicketResponse(BaseModel):
    id: str


class GetTicketDataRequest(BaseModel):
    id: str


class GetTicketDataResponse(BaseModel):
    id: str
    question: str
    status: TicketStatus
    created_at: str
    updated_at: str
    answer: Optional[str] = None


class GetTicketStatusRequest(BaseModel):
    id: str


class GetTicketStatusResponse(BaseModel):
    id: str
    status: TicketStatus
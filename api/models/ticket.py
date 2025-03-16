from pydantic import BaseModel, Field
from typing import Optional
from models.ticket import TicketStatus


class CreateTicketRequest(BaseModel):
    """Request model for creating a ticket"""
    question: str = Field(..., description="The question to be processed by LLM")


class CreateTicketResponse(BaseModel):
    """Response model for creating a ticket"""
    id: str = Field(..., description="The created ticket ID")


class GetTicketStatusRequest(BaseModel):
    """Request model for getting ticket status"""
    id: str = Field(..., description="Ticket ID to check status for")


class GetTicketStatusResponse(BaseModel):
    """Response model for ticket status"""
    id: str = Field(..., description="Ticket ID")
    status: TicketStatus = Field(..., description="Current status of the ticket")


class GetTicketDataRequest(BaseModel):
    """Request model for getting ticket data"""
    id: str = Field(..., description="Ticket ID to get data for")


class GetTicketDataResponse(BaseModel):
    """Response model for ticket data"""
    id: str = Field(..., description="Ticket ID")
    question: str = Field(..., description="Original question")
    status: TicketStatus = Field(..., description="Current status of the ticket")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    answer: Optional[str] = Field(None, description="Answer from LLM, if available")
from fastapi import APIRouter, HTTPException, status, Depends, Response
from models.ticket import TicketStatus
from core.exceptions import TicketNotFoundException
from services.ticket_service import get_ticket_service, TicketService

# Import the request/response models
from api.models.ticket import (
    CreateTicketRequest, 
    CreateTicketResponse,
    GetTicketStatusRequest, 
    GetTicketStatusResponse,
    GetTicketDataRequest, 
    GetTicketDataResponse
)

router = APIRouter(prefix="/ticket", tags=["ticket"])


async def get_ticket_service_dependency() -> TicketService:
    """Dependency for ticket service"""
    return get_ticket_service()


@router.post("/create", response_model=CreateTicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    request: CreateTicketRequest,
    ticket_service: TicketService = Depends(get_ticket_service_dependency)
):
    """Create a new ticket with a question to be processed"""
    ticket_id = await ticket_service.create_ticket(request.question)
    return CreateTicketResponse(id=ticket_id)


@router.get("/status", response_model=GetTicketStatusResponse)
async def get_ticket_status(
    id: str,
    ticket_service: TicketService = Depends(get_ticket_service_dependency)
):
    """Get the status of a ticket by ID"""
    try:
        ticket_status = await ticket_service.get_ticket_status(id)
        return GetTicketStatusResponse(id=id, status=ticket_status)
    except TicketNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID {id} not found"
        )


@router.get("/data", response_model=GetTicketDataResponse)
async def get_ticket_data(
    id: str,
    response: Response,
    ticket_service: TicketService = Depends(get_ticket_service_dependency)
):
    """Get the complete data of a ticket by ID"""
    try:
        ticket = await ticket_service.get_ticket_data(id)
        
        # Return partial content status if ticket is not done yet
        if ticket.status != TicketStatus.DONE:
            response.status_code = status.HTTP_206_PARTIAL_CONTENT
            
        return GetTicketDataResponse(
            id=ticket.id,
            question=ticket.question,
            status=ticket.status,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
            answer=ticket.answer
        )
    except TicketNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID {id} not found"
        )
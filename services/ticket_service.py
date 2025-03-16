import uuid
import asyncio
from datetime import datetime
from typing import Optional

from core.logger import logger
from core.exceptions import TicketNotFoundException
from models.ticket import Ticket, TicketStatus
from repositories.interfaces.ticket_repository_interface import TicketRepositoryInterface
from repositories.ticket_repository import get_ticket_repository
from infrastructure.messaging.interfaces.message_broker_interface import MessageBrokerInterface
from infrastructure.messaging.redis_stream import get_message_producer


class TicketService:
    """Service for ticket operations"""
    
    def __init__(
        self,
        ticket_repository: TicketRepositoryInterface = None,
        message_producer: MessageBrokerInterface = None
    ):
        self.ticket_repository = ticket_repository or get_ticket_repository()
        self.message_producer = message_producer or get_message_producer()
    
    async def create_ticket(self, question: str) -> str:
        """
        Create a new ticket and queue it for processing.
        Return the ticket ID.
        """
        # Generate UUID for ticket
        ticket_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        
        # Create ticket object
        ticket = Ticket(
            id=ticket_id,
            question=question,
            status=TicketStatus.UNINITIALIZED,
            created_at=current_time,
            updated_at=current_time
        )
        
        # Save ticket to database
        await self.ticket_repository.save_ticket(ticket)
        logger.info(f"Created ticket {ticket_id}")
        
        # Send message to processing queue
        await self.message_producer.publish("ticket.created", {"ticket_id": ticket_id})
        logger.info(f"Queued ticket {ticket_id} for processing")
        
        return ticket_id
    
    async def get_ticket_data(self, ticket_id: str) -> Optional[Ticket]:
        """
        Get ticket data by ID.
        Raises TicketNotFoundException if ticket doesn't exist.
        """
        ticket = await self.ticket_repository.get_ticket(ticket_id)
        if not ticket:
            logger.warning(f"Ticket {ticket_id} not found")
            raise TicketNotFoundException(ticket_id)
        
        return ticket
    
    async def get_ticket_status(self, ticket_id: str) -> TicketStatus:
        """
        Get status of a ticket by ID.
        Raises TicketNotFoundException if ticket doesn't exist.
        """
        ticket = await self.get_ticket_data(ticket_id)
        return ticket.status
    
    async def update_ticket_status(self, ticket_id: str, status: TicketStatus) -> None:
        """
        Update ticket status.
        Raises TicketNotFoundException if ticket doesn't exist.
        """
        ticket = await self.get_ticket_data(ticket_id)
        ticket.status = status
        ticket.updated_at = datetime.now().isoformat()
        
        await self.ticket_repository.update_ticket(ticket)
        logger.info(f"Updated ticket {ticket_id} status to {status}")
    
    async def update_ticket_answer(self, ticket_id: str, answer: str) -> None:
        """
        Update ticket with answer from LLM.
        Raises TicketNotFoundException if ticket doesn't exist.
        """
        ticket = await self.get_ticket_data(ticket_id)
        ticket.answer = answer
        ticket.status = TicketStatus.DONE
        ticket.updated_at = datetime.now().isoformat()
        
        await self.ticket_repository.update_ticket(ticket)
        logger.info(f"Updated ticket {ticket_id} with answer and status DONE")


# Factory function
def get_ticket_service():
    """Factory function to create and return a ticket service instance"""
    return TicketService()
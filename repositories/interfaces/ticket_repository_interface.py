from abc import ABC, abstractmethod
from typing import Optional
from models.ticket import Ticket


class TicketRepositoryInterface(ABC):
    """Interface for ticket repository implementations"""
    
    @abstractmethod
    async def save_ticket(self, ticket: Ticket) -> None:
        """Save a ticket to the database"""
        pass
    
    @abstractmethod
    async def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """Get a ticket by ID"""
        pass
    
    @abstractmethod
    async def update_ticket(self, ticket: Ticket) -> None:
        """Update an existing ticket"""
        pass
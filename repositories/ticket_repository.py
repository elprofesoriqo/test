import json
from typing import Optional, Dict, Any
import asyncio

from core.logger import logger
from core.exceptions import DatabaseException, TicketNotFoundException
from models.ticket import Ticket
from repositories.interfaces.ticket_repository_interface import TicketRepositoryInterface
from infrastructure.database.redis.redis_client import get_redis_client


class RedisTicketRepository(TicketRepositoryInterface):
    """Redis implementation of ticket repository"""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client or get_redis_client()
        self.key_prefix = "ticket:"
    
    async def save_ticket(self, ticket: Ticket) -> None:
        """Save ticket to Redis"""
        ticket_key = f"{self.key_prefix}{ticket.id}"
        try:
            await self.redis_client.set(ticket_key, ticket.model_dump_json())
        except Exception as e:
            logger.error(f"Error saving ticket {ticket.id}: {str(e)}")
            raise DatabaseException(f"Failed to save ticket: {str(e)}")
    
    async def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """Get ticket from Redis by id"""
        ticket_key = f"{self.key_prefix}{ticket_id}"
        
        max_retries = 3
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                ticket_data = await self.redis_client.get(ticket_key)
                
                if not ticket_data:
                    return None
                    
                return Ticket.model_validate_json(ticket_data)
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Error retrieving ticket {ticket_id}: {str(e)}")
                    raise DatabaseException(f"Failed to retrieve ticket: {str(e)}")
                
                # Exponential backoff for retries
                await asyncio.sleep(retry_delay * (2 ** attempt))
    
    async def update_ticket(self, ticket: Ticket) -> None:
        """Update existing ticket in Redis"""
        # Update the timestamp before saving
        ticket.updated_at = ticket.model_dump().get('updated_at')
        await self.save_ticket(ticket)


# Factory function to create repository
def get_ticket_repository() -> TicketRepositoryInterface:
    """Factory function to create and return a ticket repository instance"""
    return RedisTicketRepository()
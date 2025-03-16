import asyncio
from typing import Optional

from core.logger import logger
from core.config import settings
from models.ticket import TicketStatus
from services.ticket_service import get_ticket_service
from services.llm_service import get_llm_service
from infrastructure.messaging.redis_stream import get_message_consumer


class TicketProcessor:
    """Service for processing tickets asynchronously"""
    
    def __init__(self, consumer_name: str = "ticket-processor-1"):
        self.ticket_service = get_ticket_service()
        self.llm_service = get_llm_service()
        self.message_consumer = get_message_consumer(consumer_name=consumer_name)
        
    async def process_ticket(self, ticket_id: str) -> None:
        """Process a ticket by sending it to LLM and updating the ticket"""
        try:
            # Get ticket data
            ticket = await self.ticket_service.get_ticket_data(ticket_id)
            
            # Update status to PROCESSING
            await self.ticket_service.update_ticket_status(ticket_id, TicketStatus.PROCESSING)
            logger.info(f"Processing ticket {ticket_id}")
            
            # Send question to LLM
            answer = await self.llm_service.process_query(ticket.question)
            
            # Update ticket with answer and set status to DONE
            await self.ticket_service.update_ticket_answer(ticket_id, answer)
            logger.info(f"Completed processing ticket {ticket_id}")
            
        except Exception as e:
            logger.error(f"Error processing ticket {ticket_id}: {str(e)}")
    
    async def start_processing(self) -> None:
        """Start listening for ticket created events and process them"""
        logger.info("Starting ticket processor service")
        
        try:
            # Subscribe to ticket.created events
            async for message in self.message_consumer.subscribe("ticket.created"):
                ticket_id = message.get("ticket_id")
                if ticket_id:
                    # Process ticket in the background
                    asyncio.create_task(self.process_ticket(ticket_id))
                else:
                    logger.warning("Received message without ticket_id")
        except Exception as e:
            logger.error(f"Error in ticket processor: {str(e)}")
            # Wait a bit before restarting
            await asyncio.sleep(5)
            await self.start_processing()


async def run_ticket_processor():
    """Run the ticket processor service"""
    processor = TicketProcessor()
    await processor.start_processing()


if __name__ == "__main__":
    asyncio.run(run_ticket_processor())
import asyncio
from services.ticket_processor_service import TicketProcessor

async def run_ticket_processor():
    """Run the ticket processor service"""
    processor = TicketProcessor()
    await processor.start_processing()

def start_processor():
    """Synchronous function to start the async ticket processor"""
    asyncio.run(run_ticket_processor())

if __name__ == "__main__":
    start_processor()
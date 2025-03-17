import asyncio
import uuid
import json
from datetime import datetime
from typing import Dict, Any, Optional, AsyncIterator, List, Callable, Awaitable

from core.logger import logger
from core.exceptions import DatabaseException, TicketNotFoundException
from models.ticket import Ticket, TicketStatus
from repositories.interfaces.ticket_repository_interface import TicketRepositoryInterface
from infrastructure.messaging.interfaces.message_broker_interface import MessageBrokerInterface
from services.interfaces.llm_service_interface import LLMServiceInterface
from infrastructure.llm.interfaces.llm_client_interface import LLMClientInterface, LLMResponse


class InMemoryTicketRepository(TicketRepositoryInterface):
    """In-memory implementation of ticket repository"""

    def __init__(self):
        self.tickets: Dict[str, Ticket] = {}

    async def save_ticket(self, ticket: Ticket) -> None:
        """Save ticket to in-memory storage"""
        self.tickets[ticket.id] = ticket
        logger.info(f"Saved ticket {ticket.id} to in-memory storage")

    async def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """Get ticket from in-memory storage by id"""
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            return None
        return ticket

    async def update_ticket(self, ticket: Ticket) -> None:
        """Update existing ticket in in-memory storage"""
        self.tickets[ticket.id] = ticket
        logger.info(f"Updated ticket {ticket.id} in in-memory storage")


class InMemoryMessageBroker(MessageBrokerInterface):
    """In-memory implementation of message broker"""

    _messages: Dict[str, List[Dict[str, Any]]] = {}
    _callbacks: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}

    async def publish(self, topic: str, message: Dict[str, Any]) -> None:
        """Publish a message to in-memory topic"""
        if topic not in self._messages:
            self._messages[topic] = []

        self._messages[topic].append(message)
        logger.info(f"Published message to topic {topic}: {message}")

        # Notify subscribers
        if topic in self._callbacks:
            for callback in self._callbacks[topic]:
                callback(message)

    async def subscribe(self, topic: str) -> AsyncIterator[Dict[str, Any]]:
        """Subscribe to in-memory topic and yield messages"""
        # Create queue for this subscription
        queue = asyncio.Queue()

        # Register callback for this topic
        if topic not in self._callbacks:
            self._callbacks[topic] = []

        def on_message(message):
            queue.put_nowait(message)

        self._callbacks[topic].append(on_message)

        try:
            while True:
                # Wait for messages
                message = await queue.get()
                yield message
        finally:
            # Remove callback when done
            if topic in self._callbacks and on_message in self._callbacks[topic]:
                self._callbacks[topic].remove(on_message)


class InMemoryLLMClient(LLMClientInterface):
    """In-memory implementation of LLM client"""

    async def generate(self, prompt: str) -> LLMResponse:
        """Generate a mock response for the given prompt"""
        # Simulate processing delay
        await asyncio.sleep(1)

        response_text = f"This is a mock response to: '{prompt}'\n\n"
        response_text += "The answer is provided by the in-memory LLM client. "
        response_text += "In a real implementation, this would be replaced with an actual LLM response."

        return LLMResponse(text=response_text, raw_response={"mock": True})


class InMemoryLLMService(LLMServiceInterface):
    """In-memory implementation of LLM service"""

    def __init__(self):
        self.llm_client = InMemoryLLMClient()

    async def process_query(self, query: str) -> str:
        """Process query using in-memory LLM and return the answer"""
        response = await self.llm_client.generate(prompt=query)
        return response.text

    async def process_query_with_callback(
            self, query: str, on_complete: Callable[[str], Awaitable[None]]
    ) -> None:
        """Process query and call the callback when done"""
        result = await self.process_query(query)
        await on_complete(result)


class InMemoryTicketProcessor:
    """In-memory implementation of ticket processor"""

    def __init__(self):
        self.repository = InMemoryTicketRepository()
        self.llm_service = InMemoryLLMService()
        self.message_broker = InMemoryMessageBroker()
        self.started = False

    async def process_ticket(self, ticket_id: str) -> None:
        """Process a ticket using in-memory components"""
        try:
            ticket = await self.repository.get_ticket(ticket_id)
            if not ticket:
                raise TicketNotFoundException(ticket_id)

            # Update status to processing
            ticket.status = TicketStatus.PROCESSING
            ticket.updated_at = datetime.now().isoformat()
            await self.repository.update_ticket(ticket)

            # Process with LLM
            answer = await self.llm_service.process_query(ticket.question)

            # Update with answer
            ticket.answer = answer
            ticket.status = TicketStatus.DONE
            ticket.updated_at = datetime.now().isoformat()
            await self.repository.update_ticket(ticket)

            logger.info(f"Processed ticket {ticket_id} with in-memory components")
        except Exception as e:
            logger.error(f"Error processing ticket {ticket_id}: {str(e)}")

    async def start_processing(self) -> None:
        """Start processing tickets"""
        if self.started:
            return

        self.started = True
        logger.info("Starting in-memory ticket processor")

        # Start listening for messages
        asyncio.create_task(self._listen_for_tickets())

    async def _listen_for_tickets(self) -> None:
        """Listen for ticket created messages"""
        try:
            async for message in self.message_broker.subscribe("ticket.created"):
                ticket_id = message.get("ticket_id")
                if ticket_id:
                    # Process ticket in background
                    asyncio.create_task(self.process_ticket(ticket_id))
        except Exception as e:
            logger.error(f"Error in in-memory ticket processor: {str(e)}")
            self.started = False


# Create singleton instances
_ticket_repository = InMemoryTicketRepository()
_message_broker = InMemoryMessageBroker()
_llm_service = InMemoryLLMService()
_ticket_processor = InMemoryTicketProcessor()


# Mock Redis Client for compatibility
class MockRedisClient:
    """Mock Redis client that does nothing"""

    @classmethod
    async def close(cls):
        pass

    def __getattr__(self, name):
        def method(*args, **kwargs):
            return None

        return method


# Factory functions to replace Redis-dependent components
def get_ticket_repository() -> TicketRepositoryInterface:
    """Get in-memory ticket repository"""
    return _ticket_repository


def get_message_producer() -> MessageBrokerInterface:
    """Get in-memory message producer"""
    return _message_broker


def get_message_consumer(consumer_name: str) -> MessageBrokerInterface:
    """Get in-memory message consumer"""
    return _message_broker


def get_llm_service() -> LLMServiceInterface:
    """Get in-memory LLM service"""
    return _llm_service


def get_redis_client():
    """Get mock Redis client"""
    return MockRedisClient()


async def run_ticket_processor():
    """Run the in-memory ticket processor"""
    await _ticket_processor.start_processing()


def start_processor():
    """Start the in-memory ticket processor"""
    asyncio.run(run_ticket_processor())


# Apply monkeypatching
def apply_no_redis_patching():
    """Apply monkeypatching to use in-memory implementations instead of Redis"""
    import sys

    # Patch modules
    sys.modules['infrastructure.database.redis.redis_client'] = sys.modules[__name__]
    sys.modules['repositories.ticket_repository'] = sys.modules[__name__]
    sys.modules['infrastructure.messaging.redis_stream'] = sys.modules[__name__]
    sys.modules['services.llm_service'] = sys.modules[__name__]

    logger.info("Applied in-memory implementations (no Redis mode)")
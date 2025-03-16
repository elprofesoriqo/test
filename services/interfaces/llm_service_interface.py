from abc import ABC, abstractmethod
from typing import Callable, Awaitable


class LLMServiceInterface(ABC):
    """Interface for LLM service implementations"""
    
    @abstractmethod
    async def process_query(self, query: str) -> str:
        """Process a query and return the answer"""
        pass
    
    @abstractmethod
    async def process_query_with_callback(
        self, query: str, on_complete: Callable[[str], Awaitable[None]]
    ) -> None:
        """Process a query and call the callback when done"""
        pass
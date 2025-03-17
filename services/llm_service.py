import asyncio
from typing import Callable, Awaitable

from core.logger import logger
from core.exceptions import LLMServiceException
from services.interfaces.llm_service_interface import LLMServiceInterface


class LLMService(LLMServiceInterface):
    """Service for interacting with LLM"""
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
    
    async def process_query(self, query: str) -> str:
        """Process query using LLM and return the answer"""
        try:
            response = await self.llm_client.generate(prompt=query)
            return response.text
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise LLMServiceException(f"Failed to process query: {str(e)}")
    
    async def process_query_with_callback(
        self, query: str, on_complete: Callable[[str], Awaitable[None]]
    ) -> None:
        """Process query asynchronously and call the callback function when done"""
        try:
            result = await self.process_query(query)
            await on_complete(result)
        except Exception as e:
            logger.error(f"Error in process_query_with_callback: {str(e)}")
            await on_complete(f"Error processing query: {str(e)}")


def get_llm_service(llm_client=None):
    """Factory function to create and return an LLM service instance"""
    from infrastructure.llm.mock_llm_client import MockLLMClient
    
    if llm_client is None:
        llm_client = MockLLMClient()
    
    return LLMService(llm_client)
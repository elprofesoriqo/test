import asyncio
import random
from typing import Any

from core.logger import logger
from infrastructure.llm.interfaces.llm_client_interface import LLMClientInterface, LLMResponse


class MockLLMClient(LLMClientInterface):
    """Mock implementation of LLM client for testing"""
    
    async def generate(self, prompt: str) -> LLMResponse:
        """
        Generate a mock response for the given prompt.
        Simulates processing delay of 2-5 seconds.
        
        Args:
            prompt: The input prompt
            
        Returns:
            LLMResponse with generated text
        """
        # Simulate processing delay
        delay = random.uniform(2, 5)
        logger.info(f"MockLLM generating response (will take {delay:.1f}s)")
        await asyncio.sleep(delay)
        
        # Generate mock response
        response_text = f"This is a mock response to the question: '{prompt}'\n\n"
        response_text += "The answer is based on my understanding of the question. "
        response_text += "In a real implementation, this would be replaced with an actual LLM response."
        
        return LLMResponse(text=response_text, raw_response={"mock": True})
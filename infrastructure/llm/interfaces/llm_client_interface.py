from abc import ABC, abstractmethod
from typing import Any


class LLMResponse:
    """Response from LLM client"""
    def __init__(self, text: str, raw_response: Any = None):
        self.text = text
        self.raw_response = raw_response


class LLMClientInterface(ABC):
    """Interface for LLM client implementations"""
    
    @abstractmethod
    async def generate(self, prompt: str) -> LLMResponse:
        """
        Generate a response for the given prompt.
        
        Args:
            prompt: The input prompt for the LLM
            
        Returns:
            LLMResponse object containing generated text
        """
        pass
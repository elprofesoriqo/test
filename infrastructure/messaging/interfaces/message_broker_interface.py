from abc import ABC, abstractmethod
from typing import Dict, Any, AsyncIterator


class MessageBrokerInterface(ABC):
    """Interface for message broker implementations"""
    
    @abstractmethod
    async def publish(self, topic: str, message: Dict[str, Any]) -> None:
        """
        Publish a message to a topic.
        
        Args:
            topic: The topic/channel to publish to
            message: The message data to publish
        """
        pass
    
    @abstractmethod
    async def subscribe(self, topic: str) -> AsyncIterator[Dict[str, Any]]:
        """
        Subscribe to a topic and yield messages.
        
        Args:
            topic: The topic/channel to subscribe to
            
        Yields:
            Dict containing message data
        """
        pass
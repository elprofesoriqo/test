import json
import asyncio
import time
from typing import Dict, Any, AsyncIterator, Optional

from core.config import settings
from core.logger import logger
from core.exceptions import MessageBrokerException
from infrastructure.database.redis.redis_client import get_redis_client
from infrastructure.messaging.interfaces.message_broker_interface import MessageBrokerInterface


class RedisStreamProducer(MessageBrokerInterface):
    """Redis Stream implementation of message producer"""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client or get_redis_client()
        self.stream_key = settings.REDIS_STREAM_KEY
    
    async def publish(self, topic: str, message: Dict[str, Any]) -> None:
        """Publish a message to Redis Stream"""
        try:
            # Add message type to the payload
            message_data = {
                "topic": topic,
                "data": json.dumps(message),
                "timestamp": int(time.time() * 1000)
            }
            
            # Publish message to stream
            await self.redis_client.xadd(self.stream_key, message_data)
            logger.debug(f"Published message to {topic}: {message}")
        except Exception as e:
            logger.error(f"Error publishing message to {topic}: {str(e)}")
            raise MessageBrokerException(f"Failed to publish message: {str(e)}")
    
    async def subscribe(self, topic: str) -> AsyncIterator[Dict[str, Any]]:
        """
        This method is not implemented for the producer.
        Use RedisStreamConsumer for subscription.
        """
        raise NotImplementedError("RedisStreamProducer does not support subscribe operation")


class RedisStreamConsumer(MessageBrokerInterface):
    """Redis Stream implementation of message consumer"""
    
    def __init__(self, consumer_name: str, group_name: Optional[str] = None, redis_client=None):
        self.redis_client = redis_client or get_redis_client()
        self.stream_key = settings.REDIS_STREAM_KEY
        self.group_name = group_name or settings.REDIS_CONSUMER_GROUP
        self.consumer_name = consumer_name
        
    async def _ensure_consumer_group(self) -> None:
        """Ensure consumer group exists"""
        try:
            # Try to create the consumer group
            await self.redis_client.xgroup_create(
                name=self.stream_key,
                groupname=self.group_name,
                mkstream=True,
                id="0"  # Start from the beginning of the stream
            )
            logger.info(f"Created consumer group {self.group_name} for stream {self.stream_key}")
        except Exception:
            # Group may already exist, which is fine
            pass
    
    async def publish(self, topic: str, message: Dict[str, Any]) -> None:
        """
        This method is not implemented for the consumer.
        Use RedisStreamProducer for publishing.
        """
        raise NotImplementedError("RedisStreamConsumer does not support publish operation")
    
    async def subscribe(self, topic: str) -> AsyncIterator[Dict[str, Any]]:
        """Subscribe to Redis Stream and yield messages matching the topic"""
        await self._ensure_consumer_group()
        
        # Start with > to get only new messages
        last_id = ">"
        
        while True:
            try:
                # Read new messages from stream
                streams = await self.redis_client.xreadgroup(
                    groupname=self.group_name,
                    consumername=self.consumer_name,
                    streams={self.stream_key: last_id},
                    count=1,
                    block=5000  # Block for 5 seconds
                )
                
                # Process messages if any
                if streams:
                    for stream_data in streams:
                        stream_name, messages = stream_data
                        
                        for message_id, message_data in messages:
                            # Parse message data
                            message_topic = message_data.get("topic")
                            
                            # Only process messages for the requested topic
                            if message_topic == topic:
                                try:
                                    message_payload = json.loads(message_data.get("data", "{}"))
                                    logger.debug(f"Received message {message_id} for topic {topic}")
                                    
                                    # Yield the message to the caller
                                    yield message_payload
                                    
                                    # Acknowledge the message
                                    await self.redis_client.xack(
                                        self.stream_key, 
                                        self.group_name, 
                                        message_id
                                    )
                                except json.JSONDecodeError:
                                    logger.error(f"Invalid JSON in message {message_id}")
                                    # Acknowledge bad messages to avoid reprocessing
                                    await self.redis_client.xack(
                                        self.stream_key, 
                                        self.group_name, 
                                        message_id
                                    )
            except Exception as e:
                logger.error(f"Error reading from stream: {str(e)}")
                # Wait a bit before retrying
                await asyncio.sleep(1)


# Factory functions
def get_message_producer() -> MessageBrokerInterface:
    """Get message producer instance"""
    return RedisStreamProducer()


def get_message_consumer(consumer_name: str) -> MessageBrokerInterface:
    """Get message consumer instance"""
    return RedisStreamConsumer(consumer_name=consumer_name)
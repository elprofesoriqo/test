import os
from typing import Any, Dict, Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Gradient Chatbot Backend"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    
    # Redis settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    
    # Redis stream settings
    REDIS_STREAM_KEY: str = os.getenv("REDIS_STREAM_KEY", "ticket-stream")
    REDIS_CONSUMER_GROUP: str = os.getenv("REDIS_CONSUMER_GROUP", "ticket-processors")
    
    # LLM settings
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_API_URL: str = os.getenv("LLM_API_URL", "")
    
    class Config:
        env_file = ".env"


settings = Settings()
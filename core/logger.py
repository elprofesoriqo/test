import logging
import sys
from typing import Dict, Any

from core.config import settings


def setup_logging() -> logging.Logger:
    """Set up application logging"""
    logger = logging.getLogger("app")
    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(handler)
    
    return logger


logger = setup_logging()
"""
Run the application without Redis dependency
"""
import asyncio
import os
import sys

os.environ["USE_REDIS"] = "false"

import noredis

noredis.apply_no_redis_patching()

import uvicorn
from multiprocessing import Process
from worker import start_processor
from core.logger import logger

if __name__ == "__main__":
    logger.info("Starting application in no-Redis mode")
    processor = Process(target=start_processor)
    processor.start()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
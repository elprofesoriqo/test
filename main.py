import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.logger import logger
from api.endpoints.ticket import router as ticket_router

import uvicorn
from multiprocessing import Process
from worker import start_processor


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting application")

    yield

    # Shutdown
    from infrastructure.database.redis.redis_client import RedisClient
    logger.info("Shutting down application")
    await RedisClient.close()


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ticket_router)


@app.get("/")
async def root():
    return {"message": "Gradient Chatbot Backend API", "status": "running"}


if __name__ == "__main__":

    processor = Process(target=start_processor)
    processor.start()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
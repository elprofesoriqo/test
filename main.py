import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.logger import logger
from api.endpoints.ticket import router as ticket_router


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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify the actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ticket_router)


@app.get("/")
async def root():
    return {"message": "Gradient Chatbot Backend API", "status": "running"}


# In main.py where you're starting the process
if __name__ == "__main__":
    import uvicorn
    from multiprocessing import Process

    # Import the synchronous function
    from worker import start_processor

    # Start ticket processor in a separate process
    processor = Process(target=start_processor)
    processor.start()

    # Start FastAPI server
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
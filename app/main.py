from fastapi import FastAPI
from api.endpoints import router as api_router
from core.database import init_db
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event to initialize the database.
    This will create all tables in the database.
    """
    await init_db()
    print("Database initialized successfully!")

    yield
    # Shutdown
    # logger.info("Shutting down Market Data Service...")
    
    # await streaming_service.stop()
    # Cleanup code can be added here if needed
print("Market Data Service is running...")
app = FastAPI(lifespan=lifespan)

@app.get("/")
def simple_api():
    return {"message": "Hello, World!"}

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
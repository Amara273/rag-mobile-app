import os
import logging
from contextlib import asynccontextmanager 
# 
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
# 
from schemas import Base
from routers import auth_router, history_router, media_router, chat
from database import engine
# from ml_model import get_model

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Connecting to Supabase...")
    try:
        with engine.connect() as conn:
            logger.info("Database connected successfully.")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
    yield
    logger.info("Shutting down...")
    
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(history_router.router)
app.include_router(media_router.router)
app.include_router(chat.router)


@app.get("/")
def read_root():
    return {"details": "API is running"}

@app.get("/health")
def check_status():
    return {
        "detail": "healthy",
        "model_loaded" : hasattr(app.state, "model")
    }


if __name__ == "__main__":
    uvicorn.run("main:app",host="0.0.0.0", port=8000, log_level="info")
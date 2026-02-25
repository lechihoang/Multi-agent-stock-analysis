import os
import sys
import logging
from contextlib import asynccontextmanager

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.config.settings import settings
from backend.api.routes import router as api_router

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Stock Research Agent API")
    logger.info(f"LLM Model: {settings.nvidia_model}")
    logger.info(f"Rate Limit: {settings.max_requests_per_minute} req/min")

    yield

    logger.info("Shutting down Stock Research Agent API")


app = FastAPI(
    title="Stock Research Agent API",
    description="AI-powered stock research using CrewAI and Nvidia NIM",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


ui_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(ui_path):
    app.mount("/static", StaticFiles(directory=ui_path), name="static")


@app.get("/")
async def root():
    index_path = os.path.join(ui_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "name": "Stock Research Agent",
        "version": "1.0.0",
        "description": "AI-powered stock research using CrewAI and Nvidia NIM",
        "endpoints": {
            "api": "/api",
            "health": "/api/health",
            "docs": "/docs",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )

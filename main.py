from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import httpx
from datetime import datetime
from typing import Dict, List, Optional
import logging
from pydantic import BaseModel

from services.trend_analyzer import TrendAnalyzer
from services.content_generator import ContentGenerator
from services.scheduler import SchedulerService
from config.settings import LOGS_DIR

# Initialize FastAPI app
app = FastAPI(title="Bluesky Bot API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
trend_analyzer = TrendAnalyzer()
content_generator = ContentGenerator()
scheduler = SchedulerService()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / "api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Background tasks dict to track status
running_tasks = {}

# Pydantic models for request/response
class ServiceStatus(BaseModel):
    service: str
    status: str
    last_run: Optional[datetime]
    next_run: Optional[datetime]
    running: bool

class TrendAnalysisResponse(BaseModel):
    trending_topics: List[str]
    analyzed_posts: int
    timestamp: datetime

class ContentGenerationResponse(BaseModel):
    post_uri: Optional[str]
    topics_used: List[str]
    timestamp: datetime

# Scheduled task handlers
async def run_trend_analysis():
    """Run trend analysis cycle"""
    try:
        await trend_analyzer.run_analysis_cycle()
        logger.info("Scheduled trend analysis completed successfully")
    except Exception as e:
        logger.error(f"Scheduled trend analysis failed: {str(e)}")

async def run_content_generation():
    """Run content generation cycle"""
    try:
        await content_generator.run_posting_cycle()
        logger.info("Scheduled content generation completed successfully")
    except Exception as e:
        logger.error(f"Scheduled content generation failed: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Start scheduled tasks on application startup"""
    scheduler.start()
    # Schedule trend analysis every 2 hours
    await scheduler.schedule_task("trend_analysis", run_trend_analysis, interval_minutes=2)
    # Schedule content generation every 1 hour
    await scheduler.schedule_task("content_generation", run_content_generation, interval_minutes=1)

@app.on_event("shutdown")
async def shutdown_event():
    """Stop scheduler on application shutdown"""
    await scheduler.stop()

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Bluesky Bot API is running"}

@app.get("/scheduler/status")
async def get_scheduler_status():
    """Get status of all scheduled tasks"""
    return {
        "trend_analysis": scheduler.get_task_status("trend_analysis"),
        "content_generation": scheduler.get_task_status("content_generation")
    }

@app.post("/scheduler/stop")
async def stop_scheduler():
    """Stop all scheduled tasks"""
    await scheduler.stop()
    return {"message": "Scheduler stopped"}

@app.post("/scheduler/start")
async def start_scheduler():
    """Start all scheduled tasks"""
    if not scheduler.is_running:
        scheduler.start()
        await startup_event()
        return {"message": "Scheduler started"}
    return {"message": "Scheduler is already running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Check mention service health
    try:
        async with httpx.AsyncClient() as client:
            mention_response = await client.get("http://localhost:8001/status")
            mention_status = "healthy" if mention_response.status_code == 200 else "unhealthy"
    except Exception as e:
        mention_status = "unavailable"
        logger.error(f"Failed to check mention service health: {str(e)}")
    
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "services": {
            "trend_analysis": trend_analyzer.is_healthy(),
            "content_generation": content_generator.is_healthy(),
            "mention_service": mention_status,
            "scheduler": scheduler.is_running
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
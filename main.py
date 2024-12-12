import logging
from fastapi import FastAPI, BackgroundTasks, HTTPException
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import uvicorn
from typing import Dict, List

from blusky_api.client import BlueskyClient
from agent.roast_agent import RoastBobAgent
from services.blusky_trend_service import BlueskyTrendResearcher
from services.personality_posting_service import PersonalityPostingService
from config import Config

# Initialize Configuration
Config.setup_logging()
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Roast Bob - Bluesky Bot",
    description="A sassy Bluesky bot that roasts trending topics",
    version="1.0.0"
)

# Initialize services
try:
    bluesky_client = BlueskyClient()
    roast_agent = RoastBobAgent(debug=Config.DEBUG)
    trend_researcher = BlueskyTrendResearcher(bluesky_client)
    personality_service = PersonalityPostingService(
        bluesky_client,
        roast_agent,
        trend_researcher
    )
except Exception as e:
    logger.error(f"Failed to initialize services: {e}")
    raise

# Initialize scheduler
scheduler = AsyncIOScheduler()

async def scheduled_post():
    """Scheduled task for generating and posting content"""
    try:
        post_uri = personality_service.generate_and_post()
        logger.info(f"Scheduled post created: {post_uri}")
    except Exception as e:
        logger.error(f"Scheduled post failed: {e}")

async def scheduled_trend_research():
    """Scheduled task for trend research"""
    try:
        trends = trend_researcher.research_trends()
        logger.info(f"Trend research completed: {len(trends.get('trends', []))} trends found")
    except Exception as e:
        logger.error(f"Trend research failed: {e}")

@app.on_event("startup")
async def start_scheduler():
    """Start the background scheduler on app startup"""
    try:
        # Schedule periodic posts
        scheduler.add_job(
            scheduled_post,
            'interval',
            minutes=Config.POST_INTERVAL_MINUTES,
            next_run_time=datetime.now()
        )
        
        # Schedule trend research
        scheduler.add_job(
            scheduled_trend_research,
            'interval',
            minutes=Config.TREND_RESEARCH_INTERVAL_MINUTES,
            next_run_time=datetime.now()
        )
        
        scheduler.start()
        logger.info("Scheduler started successfully")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_scheduler():
    """Shutdown the scheduler when the app closes"""
    scheduler.shutdown()

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/trends")
async def get_trends():
    """Get current trends"""
    try:
        trends = trend_researcher.research_trends()
        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/post")
async def create_post(background_tasks: BackgroundTasks):
    """Trigger a new post generation"""
    try:
        background_tasks.add_task(scheduled_post)
        return {"status": "Post generation scheduled"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
async def get_post_history(limit: int = 10):
    """Get recent post history"""
    try:
        history = personality_service.get_posting_history(limit)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config")
async def get_config():
    """Get current configuration"""
    return {
        "post_interval": Config.POST_INTERVAL_MINUTES,
        "trend_interval": Config.TREND_RESEARCH_INTERVAL_MINUTES,
        "personality": Config.load_personality(),
        "debug": Config.DEBUG
    }

if __name__ == "__main__":
    try:
        Config.validate()
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=Config.DEBUG
        )
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        raise
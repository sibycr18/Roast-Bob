from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from redis import Redis
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import logging
from pydantic import BaseModel
import signal
from clients.bluesky_client import BlueskyClient
from clients.openai_client import OpenAIClient
from utils.detailed_logger import mention_logger as logger

app = FastAPI(title="Mention Service")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis setup
redis_client = Redis(host='localhost', port=6379, db=0)
MENTIONS_QUEUE = "mentions_queue"
PROCESSED_SET = "processed_mentions"

# Service state
SERVICE_STATE = {
    "is_running": False,
    "last_check": None,
    "last_error": None,
    "mentions_processed": 0,
    "background_task": None
}

class MentionService:
    def __init__(self):
        logger.info("Initializing MentionService")
        self.bluesky = BlueskyClient()
        self.openai = OpenAIClient()
        self._initialize_from_redis()

    def _initialize_from_redis(self):
        """Initialize service state from Redis"""
        logger.info("Initializing from Redis")
        try:
            # Restore cursor state if available
            cursor_state = redis_client.get('last_cursor_state')
            if cursor_state:
                state = json.loads(cursor_state.decode('utf-8'))
                self.bluesky.set_cursor(state.get('cursor'))
                logger.info("Restored cursor state from Redis", cursor_state=state)
            else:
                logger.info("No cursor state found in Redis")
        except Exception as e:
            logger.error("Failed to initialize from Redis", error=e)

    async def check_and_process_mentions(self):
        """Check for new mentions and process them"""
        try:
            logger.info("Starting mention check cycle")
            mentions = self.bluesky.get_mentions()
            
            if not mentions:
                logger.info("No new mentions found")
                return
            
            logger.info("Found mentions to process", count=len(mentions))
            processed_count = 0
            for mention in mentions:
                logger.debug("Processing mention", mention_uri=mention['uri'], author=mention['author'])
                
                # Check if already processed
                if not redis_client.sismember(PROCESSED_SET, mention['uri']):
                    if await self.process_mention(mention):
                        # Store processed mention URI with TTL (7 days)
                        redis_client.sadd(PROCESSED_SET, mention['uri'])
                        redis_client.expire(mention['uri'], 7 * 24 * 60 * 60)
                        processed_count += 1
                else:
                    logger.debug("Mention already processed", mention_uri=mention['uri'])
            
            SERVICE_STATE["mentions_processed"] += processed_count
            SERVICE_STATE["last_check"] = datetime.now()
            logger.info("Completed mention check cycle", processed_count=processed_count)
            
        except Exception as e:
            SERVICE_STATE["last_error"] = str(e)
            logger.error("Error in mention check cycle", error=e)

    async def process_mention(self, mention: Dict) -> bool:
        """Process a single mention"""
        logger.debug("Processing individual mention", mention_uri=mention['uri'])
        try:
            # Generate response
            logger.info("Generating response for mention", mention_text=mention['text'][:100])
            response = await self.openai.generate_response({
                'current_post': mention['text'],
                'parent_post': await self._get_parent_post(mention['reply_to']) if mention.get('reply_to') else None,
                'author': mention['author']
            })
            
            # Post response
            logger.info("Posting response to Bluesky", response_text=response[:100])
            post_uri = self.bluesky.post_skeet(
                text=response,
                reply_to=mention['reply_to']
            )
            
            logger.info("Successfully processed mention", 
                       author=mention['author'], 
                       mention_text=mention['text'][:50],
                       response_uri=post_uri)
            return True
            
        except Exception as e:
            logger.error("Failed to process mention", error=e, mention_uri=mention['uri'])
            return False

    async def _get_parent_post(self, uri: str) -> Optional[str]:
        """Fetch parent post text"""
        logger.debug("Fetching parent post", uri=uri)
        try:
            post = self.bluesky.get_post(uri)
            if post:
                logger.debug("Successfully retrieved parent post", post_text=post.get('text', '')[:50])
            else:
                logger.debug("Parent post not found", uri=uri)
            return post.get('text') if post else None
        except Exception as e:
            logger.error("Failed to get parent post", error=e, uri=uri)
            return None

    async def continuous_mention_check(self):
        """Continuously check for mentions every 5 minutes"""
        logger.info("Starting continuous mention check")
        SERVICE_STATE["is_running"] = True
        
        while SERVICE_STATE["is_running"]:
            logger.debug("Running mention check cycle")
            await self.check_and_process_mentions()
            
            # Wait 5 minutes before next check
            logger.debug("Waiting for next check cycle")
            await asyncio.sleep(20)  # 5 minutes in seconds

# Initialize service
mention_service = MentionService()

@app.on_event("startup")
async def startup_event():
    """Start the continuous mention checking on startup"""
    logger.info("Starting mention service")
    SERVICE_STATE["background_task"] = asyncio.create_task(
        mention_service.continuous_mention_check()
    )

@app.on_event("shutdown")
async def shutdown_event():
    """Clean shutdown of the service"""
    logger.info("Shutting down mention service")
    SERVICE_STATE["is_running"] = False
    if SERVICE_STATE["background_task"]:
        SERVICE_STATE["background_task"].cancel()
        try:
            await SERVICE_STATE["background_task"]
        except asyncio.CancelledError:
            logger.info("Background task cancelled")

@app.get("/status")
async def get_status():
    """Get current service status"""
    logger.debug("Status check requested")
    status = {
        "is_running": SERVICE_STATE["is_running"],
        "last_check": SERVICE_STATE["last_check"],
        "last_error": SERVICE_STATE["last_error"],
        "mentions_processed": SERVICE_STATE["mentions_processed"],
        "next_check": (
            SERVICE_STATE["last_check"] + timedelta(minutes=5)
            if SERVICE_STATE["last_check"]
            else None
        )
    }
    logger.info("Returning service status", status=status)
    return status

@app.post("/start")
async def start_service():
    """Start the mention service if it's not running"""
    logger.info("Service start requested")
    if not SERVICE_STATE["is_running"]:
        SERVICE_STATE["background_task"] = asyncio.create_task(
            mention_service.continuous_mention_check()
        )
        logger.info("Service started successfully")
        return {"message": "Service started"}
    logger.info("Service already running")
    return {"message": "Service is already running"}

@app.post("/stop")
async def stop_service():
    """Stop the mention service"""
    logger.info("Service stop requested")
    if SERVICE_STATE["is_running"]:
        SERVICE_STATE["is_running"] = False
        if SERVICE_STATE["background_task"]:
            SERVICE_STATE["background_task"].cancel()
        logger.info("Service stopped successfully")
        return {"message": "Service stopped"}
    logger.info("Service was not running")
    return {"message": "Service is not running"}

@app.get("/stats")
async def get_stats():
    """Get service statistics"""
    logger.debug("Stats requested")
    stats = {
        "total_processed": SERVICE_STATE["mentions_processed"],
        "processed_mentions": list(redis_client.smembers(PROCESSED_SET)),
        "uptime": (
            datetime.now() - SERVICE_STATE["last_check"]
            if SERVICE_STATE["last_check"]
            else None
        )
    }
    logger.info("Returning service stats", stats=stats)
    return stats

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting mention service server")
    uvicorn.run(app, host="0.0.0.0", port=8001)
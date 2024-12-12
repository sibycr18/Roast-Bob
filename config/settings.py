import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs"

# Create logs directory if it doesn't exist
LOGS_DIR.mkdir(exist_ok=True)

# Log file paths
MENTION_LOG = LOGS_DIR / "mentions.log"
TREND_LOG = LOGS_DIR / "trends.log"
CONTENT_LOG = LOGS_DIR / "content.log"
MEMORY_LOG = LOGS_DIR / "memory.log"

# API Credentials
BLUESKY_HANDLE = os.getenv("BLUESKY_HANDLE")
BLUESKY_PASSWORD = os.getenv("BLUESKY_PASSWORD")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Bot Configuration
POSTING_INTERVAL_HOURS = int(os.getenv("POSTING_INTERVAL_HOURS", "1"))
MAX_RESPONSE_LENGTH = 280  # Bluesky character limit
FEED_LIMIT = 100  # Maximum number of feed items to analyze

# OpenAI Configuration
GPT_MODEL = "gpt-3.5-turbo"
GPT_TEMPERATURE = 0.9  # Higher temperature for more creative responses
MAX_TOKENS = 150  # Ensures responses stay within Bluesky limit

# Bot Personality
BOT_PERSONA = """You are a humorous and opinionated individual who has something to say about everything. 
Your responses should be witty, sometimes sarcastic, and always entertaining. 
When asked to roast something, you become savagely critical without holding back."""

# ChromaDB Configuration
CHROMA_PERSIST_DIR = BASE_DIR / "chroma_db"
COLLECTION_NAME = "bluesky_trends"

# Error messages
ERRORS = {
    "auth_failed": "Authentication failed: {}",
    "post_failed": "Failed to post content: {}",
    "api_limit": "API rate limit reached: {}",
    "memory_error": "Failed to access memory store: {}",
    "invalid_env": "Missing required environment variables"
}

# Validate required environment variables
required_vars = ["BLUESKY_HANDLE", "BLUESKY_PASSWORD", "OPENAI_API_KEY"]
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
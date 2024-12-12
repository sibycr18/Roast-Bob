import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any
import logging
import json

# Load environment variables
load_dotenv()

class Config:
    """Configuration management for the application"""
    
    # Base configuration
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    ENV = os.getenv('ENV', 'development')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Bluesky credentials
    BLUESKY_HANDLE = os.getenv('BLUESKY_HANDLE')
    BLUESKY_PASSWORD = os.getenv('BLUESKY_PASSWORD')
    
    # Rate limiting
    RATE_LIMIT_MAX_REQUESTS = int(os.getenv('RATE_LIMIT_MAX_REQUESTS', '50'))
    RATE_LIMIT_WINDOW_MINUTES = int(os.getenv('RATE_LIMIT_WINDOW_MINUTES', '15'))
    
    # Scheduling
    POST_INTERVAL_MINUTES = int(os.getenv('POST_INTERVAL_MINUTES', '60'))
    TREND_RESEARCH_INTERVAL_MINUTES = int(os.getenv('TREND_RESEARCH_INTERVAL_MINUTES', '60'))
    
    # ChromaDB
    CHROMADB_PERSISTENCE_PATH = os.getenv('CHROMADB_PERSISTENCE_PATH', './data/chromadb')
    
    # Personality settings
    DEFAULT_PERSONALITY = {
        "sass_level": 0.8,
        "trend_awareness": 0.7,
        "memory_usage": 0.3
    }

    @classmethod
    def load_personality(cls) -> Dict[str, float]:
        """Load personality settings from file or return defaults"""
        personality_path = Path("config/personality.json")
        
        if personality_path.exists():
            try:
                with open(personality_path) as f:
                    return json.load(f)
            except Exception as e:
                logging.warning(f"Failed to load personality config: {e}")
        
        return cls.DEFAULT_PERSONALITY

    @classmethod
    def save_personality(cls, settings: Dict[str, float]):
        """Save personality settings to file"""
        personality_path = Path("config/personality.json")
        
        try:
            personality_path.parent.mkdir(exist_ok=True)
            with open(personality_path, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save personality config: {e}")

    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        required_vars = [
            'BLUESKY_HANDLE',
            'BLUESKY_PASSWORD'
        ]
        
        missing = [var for var in required_vars if not getattr(cls, var)]
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        return True

    @classmethod
    def setup_logging(cls):
        """Configure logging based on environment"""
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(f"logs/{cls.ENV}.log")
            ]
        )

    @classmethod
    def get_all(cls) -> Dict[str, Any]:
        """Get all configuration as dictionary"""
        return {
            key: value for key, value in vars(cls).items()
            if not key.startswith('_') and isinstance(value, (str, int, float, bool, dict))
        }
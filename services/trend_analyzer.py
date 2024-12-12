import logging
from typing import List, Dict, Optional
from datetime import datetime, timezone
import asyncio
from config.settings import (
    FEED_LIMIT,
    TREND_LOG
)
from clients.bluesky_client import BlueskyClient
from clients.openai_client import OpenAIClient
from services.memory_service import MemoryService

class TrendAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        
        # Initialize clients
        self.bluesky = BlueskyClient()
        self.openai = OpenAIClient()
        self.memory = MemoryService()
        
        # Track last analyzed post to avoid duplicates
        self.last_analyzed_timestamp = None

    def _setup_logging(self):
        """Configure logging for trend analyzer"""
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler = logging.FileHandler(TREND_LOG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.INFO)

    def _should_analyze_post(self, post: Dict) -> bool:
        """
        Determine if a post should be analyzed based on criteria:
        - Not previously analyzed
        - Not a reply (unless it's generating significant engagement)
        - Not from the bot itself
        """
        if self.last_analyzed_timestamp and post['timestamp'] <= self.last_analyzed_timestamp:
            return False
            
        # Skip posts from the bot itself
        if post['author'] == self.bluesky.handle:
            return False
            
        # For now, analyze all other posts
        return True

    async def _analyze_post(self, post: Dict) -> Optional[Dict]:
        """Analyze a single post using OpenAI"""
        try:
            # Generate analysis using OpenAI
            analysis = await self.openai.generate_trend_analysis(post['text'])
            
            # Store in memory
            self.memory.store_analysis(post, analysis)
            
            self.logger.info(f"Analyzed post from {post['author']}: {post['text'][:50]}...")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Failed to analyze post: {str(e)}")
            return None

    async def analyze_feed(self) -> List[Dict]:
        """
        Fetch and analyze feed content
        Returns: List of analyzed posts with their trends
        """
        try:
            # Get feed items
            feed_items = self.bluesky.get_feed(limit=FEED_LIMIT)
            
            if not feed_items:
                self.logger.warning("No feed items retrieved")
                return []

            analyzed_posts = []
            analysis_tasks = []

            # Create analysis tasks for relevant posts
            for post in feed_items:
                if self._should_analyze_post(post):
                    analysis_tasks.append(self._analyze_post(post))

            # Run analyses concurrently
            if analysis_tasks:
                analyses = await asyncio.gather(*analysis_tasks, return_exceptions=True)
                
                # Filter out failed analyses
                for post, analysis in zip(feed_items, analyses):
                    if isinstance(analysis, Exception):
                        self.logger.error(f"Analysis failed for post: {str(analysis)}")
                        continue
                    if analysis:
                        analyzed_posts.append({
                            "post": post,
                            "analysis": analysis
                        })

                # Update last analyzed timestamp
                if analyzed_posts:
                    self.last_analyzed_timestamp = max(
                        post['post']['timestamp'] 
                        for post in analyzed_posts
                    )

            # Persist memory after batch analysis
            self.memory.persist()
            
            self.logger.info(f"Analyzed {len(analyzed_posts)} new posts")
            return analyzed_posts

        except Exception as e:
            self.logger.error(f"Feed analysis failed: {str(e)}")
            return []

    async def get_trending_topics(self) -> List[str]:
        """
        Get current trending topics from analyzed content
        Returns: List of trending topics
        """
        try:
            # Get recent analyses from memory
            recent_trends = self.memory.get_recent_trends(limit=20)
            
            # Extract and count topics
            topic_counts = {}
            for trend in recent_trends:
                for topic in trend['topics']:
                    topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
            # Sort topics by frequency
            trending_topics = sorted(
                topic_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Return top topics
            return [topic for topic, _ in trending_topics[:10]]
            
        except Exception as e:
            self.logger.error(f"Failed to get trending topics: {str(e)}")
            return []

    async def get_bot_opinions(self, topic: str) -> List[str]:
        """
        Get bot's stored opinions on a specific topic
        Returns: List of relevant opinions
        """
        try:
            similar_content = self.memory.find_similar_content(topic)
            return [item['opinion'] for item in similar_content]
            
        except Exception as e:
            self.logger.error(f"Failed to get opinions for topic {topic}: {str(e)}")
            return []

    async def run_analysis_cycle(self):
        """Run a complete analysis cycle"""
        try:
            self.logger.info("Starting analysis cycle")
            
            # Analyze feed content
            analyzed_posts = await self.analyze_feed()
            
            # Get trending topics
            trending_topics = await self.get_trending_topics()
            
            self.logger.info(f"Analysis cycle completed. Found {len(trending_topics)} trending topics")
            
            return {
                "analyzed_posts": analyzed_posts,
                "trending_topics": trending_topics
            }
            
        except Exception as e:
            self.logger.error(f"Analysis cycle failed: {str(e)}")
            return None
import os
from dotenv import load_dotenv
from atproto import Client
import logging
from typing import List, Optional, Dict
from datetime import datetime

class BlueskyClient:
    def __init__(self):
        load_dotenv()
        self.handle = os.getenv('BLUESKY_HANDLE')
        self.password = os.getenv('BLUESKY_PASSWORD')
        self.logger = logging.getLogger(__name__)
        
        if not all([self.handle, self.password]):
            raise ValueError("Bluesky credentials not found in environment")
        
        self.client = Client()
        self._authenticate()

    def _authenticate(self):
        """Handle authentication with error logging"""
        try:
            self.client.login(self.handle, self.password)
            self.logger.info(f"Successfully logged in as {self.handle}")
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            raise

    def post_skeet(self, text: str, reply_to: Optional[str] = None) -> str:
        """Post content to Bluesky"""
        try:
            post = self.client.send_post(text=text, reply_to=reply_to)
            self.logger.info(f"Posted content: {text[:50]}...")
            return post.uri
        except Exception as e:
            self.logger.error(f"Failed to post: {e}")
            raise

    def get_mentions(self, limit: int = 20) -> List[Dict]:
        """Get recent mentions"""
        try:
            mentions = self.client.app.bsky.notification.list_notifications()
            filtered_mentions = [
                {
                    'author': mention.author.handle,
                    'text': mention.record.text,
                    'uri': mention.uri,
                    'timestamp': mention.indexed_at
                }
                for mention in mentions.notifications
                if mention.reason == 'mention'
            ][:limit]
            return filtered_mentions
        except Exception as e:
            self.logger.error(f"Failed to get mentions: {e}")
            raise

    def get_feed(self, limit: int = 20) -> List[Dict]:
        """Get feed items"""
        try:
            feed = self.client.app.bsky.feed.get_timeline()
            feed_items = [
                {
                    'author': item.post.author.handle,
                    'text': item.post.record.text,
                    'uri': item.post.uri,
                    'timestamp': item.post.indexed_at
                }
                for item in feed.feed
            ][:limit]
            return feed_items
        except Exception as e:
            self.logger.error(f"Failed to get feed: {e}")
            raise
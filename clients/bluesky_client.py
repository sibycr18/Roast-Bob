import os
from dotenv import load_dotenv
from atproto import Client, exceptions
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import backoff
from utils.logger import get_logger


class BlueskyClient:
    def __init__(self):
        """Initialize Bluesky client with environment credentials"""
        load_dotenv()
        self.handle = os.getenv('BLUESKY_HANDLE')
        self.password = os.getenv('BLUESKY_PASSWORD')
        self.logger = get_logger(__name__)
        self._last_cursor = None  # Add cursor tracking
        
        if not all([self.handle, self.password]):
            raise ValueError("Bluesky credentials not found in environment")
        
        self.client = Client()
        self._authenticate()

    @backoff.on_exception(
        backoff.expo,
        (exceptions.AtProtocolError),
        max_tries=3
    )

    def get_mentions(self, limit: int = 20) -> Dict[str, Any]:
        """Get recent mentions using the notifications API with cursor support"""
        try:
            # Add cursor to the request if we have one
            params = {'limit': limit}
            if self._last_cursor:
                params['cursor'] = self._last_cursor

            response = self.client.app.bsky.notification.list_notifications(params)
            
            # Update cursor for next request
            self._last_cursor = getattr(response, 'cursor', None)
            
            filtered_mentions = []
            for notification in response.notifications:
                # Only process mention notifications
                if notification.reason == 'mention':
                    # Extract text and reply data from the record
                    text = getattr(notification.record, 'text', '')
                    reply_data = self._extract_reply_data(notification.record)
                    
                    mention_data = {
                        'author': self._extract_author_data(notification.author),
                        'text': text,
                        'uri': notification.uri,
                        'cid': notification.cid,
                        'timestamp': notification.indexed_at,
                        'reply_to': reply_data.get('parent_uri') if reply_data else None,
                        'root': reply_data.get('root_uri') if reply_data else None,
                        'is_read': notification.is_read,
                        'labels': getattr(notification, 'labels', []),
                    }
                    filtered_mentions.append(mention_data)
            
            filtered_mentions = filtered_mentions[:limit]
            self.logger.info(f"Retrieved {len(filtered_mentions)} mentions")
            
            return {
                'mentions': filtered_mentions,
                'cursor': self._last_cursor
            }

        except Exception as e:
            self.logger.error(f"Failed to get mentions: {e}")
            raise

    def get_cursor_state(self) -> Dict:
        """Get current cursor state"""
        return {
            'cursor': self._last_cursor,
            'timestamp': self._get_rfc3339_datetime()
        }

    def set_cursor(self, cursor: str):
        """Set cursor manually if needed"""
        self._last_cursor = cursor
        self.logger.info(f"Cursor manually set to: {cursor}")


    def _authenticate(self):
        """Handle authentication with retries and proper error handling"""
        try:
            profile = self.client.login(self.handle, self.password)
            self.did = profile.did
            self.logger.info(f"Successfully logged in as {self.handle} (DID: {self.did})")
        except Exception as e:
            self.logger.error(f"Authentication failed: {str(e)}")
            raise

    def _parse_at_uri(self, uri: str) -> tuple:
        """Parse AT URI into components"""
        # Format: at://did:plc:xxx/app.bsky.feed.post/xxx
        try:
            parts = uri.split('/')
            did = parts[2]
            rkey = parts[-1]
            return did, rkey
        except Exception as e:
            self.logger.error(f"Failed to parse URI {uri}: {str(e)}")
            raise ValueError(f"Invalid AT URI format: {uri}")

    def _extract_reply_data(self, record: Any) -> Optional[Dict]:
        """Extract reply reference data from a record"""
        try:
            reply = getattr(record, 'reply', None)
            if reply:
                return {
                    'parent_uri': getattr(reply.parent, 'uri', None) if hasattr(reply, 'parent') else None,
                    'root_uri': getattr(reply.root, 'uri', None) if hasattr(reply, 'root') else None,
                }
            return None
        except Exception as e:
            self.logger.warning(f"Failed to extract reply data: {str(e)}")
            return None

    def _extract_author_data(self, author: Any) -> Dict:
        """Extract author information from profile view"""
        return {
            'did': getattr(author, 'did', None),
            'handle': getattr(author, 'handle', None),
            'display_name': getattr(author, 'display_name', None),
            'avatar': getattr(author, 'avatar', None),
            'description': getattr(author, 'description', None)
        }

    def _get_rfc3339_datetime(self) -> str:
        """Get current datetime in RFC3339 format with timezone"""
        return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    @backoff.on_exception(
        backoff.expo,
        (exceptions.AtProtocolError),
        max_tries=3
    )
    def post_skeet(self, text: str, reply_to: Optional[str] = None) -> str:
        """Post content to Bluesky with proper reply handling"""
        try:
            # Prepare reply reference if needed
            reply_ref = None
            if reply_to:
                reply_post = self.get_post(reply_to)
                if reply_post:
                    reply_ref = {
                        'root': {
                            'uri': reply_post['uri'],
                            'cid': reply_post['cid']
                        },
                        'parent': {
                            'uri': reply_post['uri'],
                            'cid': reply_post['cid']
                        }
                    }

            # Create post record
            record = {
                'text': text,
                'createdAt': self._get_rfc3339_datetime(),
                '$type': 'app.bsky.feed.post',
            }
            
            if reply_ref:
                record['reply'] = reply_ref

            # Create post
            response = self.client.com.atproto.repo.create_record({
                'repo': self.did,
                'collection': 'app.bsky.feed.post',
                'record': record
            })
            
            post_uri = f"at://{self.did}/app.bsky.feed.post/{response.uri.split('/')[-1]}"
            self.logger.info(f"Posted content: {text[:50]}...")
            return post_uri

        except Exception as e:
            self.logger.error(f"Failed to post: {str(e)}")
            raise

    @backoff.on_exception(
        backoff.expo,
        (exceptions.AtProtocolError),
        max_tries=3
    )
    def get_post(self, uri: str) -> Optional[Dict]:
        """Get a specific post by URI"""
        try:
            did, rkey = self._parse_at_uri(uri)
            
            response = self.client.com.atproto.repo.get_record({
                'collection': 'app.bsky.feed.post',
                'repo': did,
                'rkey': rkey
            })
            
            if response and response.value:
                reply_data = self._extract_reply_data(response.value)
                
                return {
                    'uri': uri,
                    'cid': response.cid,
                    'author': did,
                    'text': getattr(response.value, 'text', ''),
                    'reply_to': reply_data.get('parent_uri') if reply_data else None,
                    'root': reply_data.get('root_uri') if reply_data else None,
                    'created_at': getattr(response.value, 'createdAt', None),
                    'indexed_at': datetime.utcnow().isoformat()
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get post {uri}: {str(e)}")
            return None

    @backoff.on_exception(
        backoff.expo,
        (exceptions.AtProtocolError),
        max_tries=3
    )
    def get_mentions(self, limit: int = 20) -> List[Dict]:
        """Get recent mentions using the notifications API"""
        try:
            response = self.client.app.bsky.notification.list_notifications({'limit': limit})
            
            filtered_mentions = []
            for notification in response.notifications:
                # Only process mention notifications
                if notification.reason == 'mention':
                    # Extract text and reply data from the record
                    text = getattr(notification.record, 'text', '')
                    reply_data = self._extract_reply_data(notification.record)
                    
                    mention_data = {
                        'author': self._extract_author_data(notification.author),
                        'text': text,
                        'uri': notification.uri,
                        'cid': notification.cid,
                        'timestamp': notification.indexed_at,
                        'reply_to': reply_data.get('parent_uri') if reply_data else None,
                        'root': reply_data.get('root_uri') if reply_data else None,
                        'is_read': notification.is_read,
                        'labels': getattr(notification, 'labels', []),
                    }
                    filtered_mentions.append(mention_data)
            
            filtered_mentions = filtered_mentions[:limit]
            self.logger.info(f"Retrieved {len(filtered_mentions)} mentions")
            return filtered_mentions

        except Exception as e:
            self.logger.error(f"Failed to get mentions: {e}")
            raise

    @backoff.on_exception(
        backoff.expo,
        (exceptions.AtProtocolError),
        max_tries=3
    )
    def get_feed(self, limit: int = 20) -> List[Dict]:
        """Get feed items"""
        try:
            response = self.client.app.bsky.feed.get_timeline({'limit': limit})
            
            feed_items = []
            for item in response.feed:
                reply_data = self._extract_reply_data(item.post.record)
                
                feed_item = {
                    'author': self._extract_author_data(item.post.author),
                    'text': getattr(item.post.record, 'text', ''),
                    'uri': item.post.uri,
                    'cid': item.post.cid,
                    'timestamp': item.post.indexed_at,
                    'reply_to': reply_data.get('parent_uri') if reply_data else None,
                    'root': reply_data.get('root_uri') if reply_data else None,
                    'labels': getattr(item.post, 'labels', []),
                }
                feed_items.append(feed_item)
            
            feed_items = feed_items[:limit]
            self.logger.info(f"Retrieved {len(feed_items)} feed items")
            return feed_items

        except Exception as e:
            self.logger.error(f"Failed to get feed: {e}")
            raise

    def is_healthy(self) -> bool:
        """Check if client is authenticated and working"""
        try:
            # Try to get timeline as a health check
            self.client.app.bsky.feed.get_timeline({'limit': 1})
            return True
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return False

    def get_status(self) -> Dict:
        """Get client status information"""
        return {
            'handle': self.handle,
            'did': getattr(self, 'did', None),
            'authenticated': self.is_healthy(),
            'last_error': None,
            'api_status': 'healthy' if self.is_healthy() else 'unhealthy'
        }
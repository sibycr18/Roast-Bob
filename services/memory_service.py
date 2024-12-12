import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging
from utils.logger import get_logger
from redis import Redis

class MemoryService:
    def __init__(self):
        self.redis = Redis(host='localhost', port=6379, db=0)
        self.logger = get_logger(__name__)

    def _serialize_value(self, value: Any) -> str:
        """
        Serialize complex values into JSON strings for Redis storage
        """
        try:
            if isinstance(value, (str, int, float, bool)):
                return str(value)
            return json.dumps(value)
        except Exception as e:
            self.logger.error(f"Serialization error: {str(e)}")
            return str(value)

    def _deserialize_value(self, value_str: str) -> Any:
        """
        Deserialize values from Redis storage
        """
        try:
            return json.loads(value_str)
        except json.JSONDecodeError:
            return value_str

    def _parse_timestamp(self, timestamp_str: str) -> str:
        """
        Parse and normalize timestamp string
        """
        try:
            # Handle 'Z' timezone indicator
            if isinstance(timestamp_str, datetime):
                return timestamp_str.isoformat()
            
            if timestamp_str.endswith('Z'):
                timestamp_str = timestamp_str[:-1] + '+00:00'
            return timestamp_str
        except Exception as e:
            self.logger.error(f"Timestamp parsing error: {str(e)}")
            return datetime.now().isoformat()

    def store_analysis(self, post: Dict[str, Any], analysis: Dict[str, Any]) -> bool:
        """
        Store post and its analysis in Redis
        """
        try:
            # Create a unique key for the post
            post_key = f"post:{post.get('uri', datetime.now().isoformat())}"
            
            # Get and parse timestamp
            timestamp_str = self._parse_timestamp(post.get('timestamp', datetime.now().isoformat()))
            
            # Prepare post data
            post_data = {
                'text': str(post.get('text', '')),
                'uri': str(post.get('uri', '')),
                'timestamp': timestamp_str,
                'author': self._serialize_value(post.get('author', '')),
                'metadata': self._serialize_value({})  # Store empty dict for now to avoid type errors
            }

            # Prepare analysis data
            analysis_data = {
                'opinion': str(analysis.get('opinion', '')),
                'topics': self._serialize_value(analysis.get('topics', [])),
                'future_post_ideas': self._serialize_value(analysis.get('future_post_ideas', []))
            }

            # Store data in Redis
            self.redis.hmset(f"{post_key}:post", post_data)
            self.redis.hmset(f"{post_key}:analysis", analysis_data)
            
            # Convert timestamp to float for sorted set
            dt = datetime.fromisoformat(timestamp_str)
            self.redis.zadd('post_index', {post_key: float(dt.timestamp())})

            return True

        except Exception as e:
            self.logger.error(f"Failed to store analysis: {str(e)}")
            return False

    def get_recent_trends(self, limit: int = 20) -> List[Dict]:
        """
        Get recent trending topics and their analyses
        """
        try:
            # Get recent post keys
            post_keys = self.redis.zrevrange('post_index', 0, limit - 1)
            
            trends = []
            for post_key in post_keys:
                post_key = post_key.decode('utf-8')
                analysis_data = self.redis.hgetall(f"{post_key}:analysis")
                
                if analysis_data:
                    trends.append({
                        'topics': self._deserialize_value(analysis_data[b'topics'].decode('utf-8')),
                        'opinion': analysis_data[b'opinion'].decode('utf-8')
                    })
            
            return trends

        except Exception as e:
            self.logger.error(f"Failed to get recent trends: {str(e)}")
            return []

    def find_similar_content(self, topic: str) -> List[Dict]:
        """
        Find content similar to given topic
        """
        try:
            similar_content = []
            post_keys = self.redis.zrevrange('post_index', 0, -1)
            
            for post_key in post_keys:
                post_key = post_key.decode('utf-8')
                analysis_data = self.redis.hgetall(f"{post_key}:analysis")
                
                if analysis_data:
                    topics = self._deserialize_value(analysis_data[b'topics'].decode('utf-8'))
                    if topic.lower() in [t.lower() for t in topics]:
                        similar_content.append({
                            'opinion': analysis_data[b'opinion'].decode('utf-8'),
                            'topics': topics
                        })
            
            return similar_content[:10]  # Limit to 10 similar items

        except Exception as e:
            self.logger.error(f"Failed to find similar content: {str(e)}")
            return []

    def persist(self) -> bool:
        """
        Ensure all data is persisted to Redis
        Note: Redis automatically persists data, but this method
        can be used for any cleanup or maintenance tasks
        """
        try:
            # Cleanup old data
            cutoff = datetime.now() - timedelta(days=7)
            cutoff_timestamp = cutoff.timestamp()
            
            # Remove old entries
            old_keys = self.redis.zrangebyscore('post_index', '-inf', cutoff_timestamp)
            for key in old_keys:
                key = key.decode('utf-8')
                self.redis.delete(f"{key}:post")
                self.redis.delete(f"{key}:analysis")
                self.redis.zrem('post_index', key)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to persist data: {str(e)}")
            return False

    def get_stats(self) -> Dict:
        """
        Get memory service statistics
        """
        try:
            total_posts = self.redis.zcard('post_index')
            recent_posts = len(self.redis.zrangebyscore(
                'post_index',
                (datetime.now() - timedelta(days=1)).timestamp(),
                '+inf'
            ))
            
            return {
                'total_posts': total_posts,
                'recent_posts': recent_posts,
                'status': 'healthy'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get stats: {str(e)}")
            return {
                'total_posts': 0,
                'recent_posts': 0,
                'status': 'error',
                'error': str(e)
            }
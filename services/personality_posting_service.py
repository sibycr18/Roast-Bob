import chromadb
import logging
from datetime import datetime
from typing import Optional, Dict, List
import random

class PersonalityPostingService:
    def __init__(
        self,
        bluesky_client,
        roast_agent,
        trend_researcher,
        memory_collection_name: str = "personality_memories"
    ):
        self.client = bluesky_client
        self.roast_agent = roast_agent
        self.trend_researcher = trend_researcher
        self.logger = logging.getLogger(__name__)
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.Client()
        self.memory_collection = self.chroma_client.get_or_create_collection(
            name=memory_collection_name
        )
        
        # Personality settings
        self.posting_style = {
            "trend_focus": 0.7,  # How much to focus on trends vs random topics
            "sass_level": 0.8,   # How sassy/savage to be
            "memory_usage": 0.3  # How much to reference past posts
        }

    def generate_and_post(self) -> Optional[str]:
        """Generate and post content"""
        try:
            content = self._generate_content()
            post_uri = self.client.post_skeet(content)
            self._store_memory(content, post_uri)
            return post_uri
        except Exception as e:
            self.logger.error(f"Failed to generate and post: {e}")
            return None

    def _generate_content(self) -> str:
        """Generate content based on trends and personality"""
        # Decide content strategy
        if random.random() < self.posting_style["trend_focus"]:
            return self._generate_trend_based_content()
        else:
            return self._generate_memory_based_content()

    def _generate_trend_based_content(self) -> str:
        """Generate content based on current trends"""
        trends = self.trend_researcher.research_trends()
        
        if 'error' in trends or not trends['trends']:
            return self._generate_fallback_content()
        
        # Select a trend based on engagement potential
        selected_trend = self._select_trend(trends['trends'])
        
        return self.roast_agent.generate_reply(
            tweet=self.roast_agent.Tweet(
                text=selected_trend['topic'],
                user="trend",
                timestamp=str(datetime.now())
            ),
            style="savage" if random.random() < self.posting_style["sass_level"] else "witty"
        )

    def _generate_memory_based_content(self) -> str:
        """Generate content based on past memories"""
        try:
            memories = self.memory_collection.query(
                query_texts=[""],
                n_results=5
            )
            
            if memories and memories['documents']:
                # Reference a past post
                past_post = random.choice(memories['documents'][0])
                return self.roast_agent.generate_reply(
                    tweet=self.roast_agent.Tweet(
                        text=f"Remembering {past_post}",
                        user="memory",
                        timestamp=str(datetime.now())
                    )
                )
        except Exception as e:
            self.logger.warning(f"Memory retrieval failed: {e}")
        
        return self._generate_fallback_content()

    def _generate_fallback_content(self) -> str:
        """Generate fallback content when other methods fail"""
        fallback_topics = [
            "internet culture",
            "social media",
            "tech trends",
            "digital life",
            "online drama"
        ]
        return self.roast_agent.generate_reply(
            tweet=self.roast_agent.Tweet(
                text=random.choice(fallback_topics),
                user="fallback",
                timestamp=str(datetime.now())
            )
        )

    def _select_trend(self, trends: List[Dict]) -> Dict:
        """Select a trend based on engagement potential"""
        # Weight trends by count and type
        weighted_trends = []
        for trend in trends:
            weight = trend['count']
            if trend['type'] == 'hashtag':
                weight *= 1.2
            elif trend['type'] == 'topic':
                weight *= 1.5
            weighted_trends.append((trend, weight))
        
        # Select based on weights
        total_weight = sum(w for _, w in weighted_trends)
        r = random.uniform(0, total_weight)
        current_weight = 0
        
        for trend, weight in weighted_trends:
            current_weight += weight
            if current_weight > r:
                return trend
        
        return trends[0]  # Fallback to first trend

    def _store_memory(self, content: str, post_uri: str):
        """Store post in ChromaDB memory"""
        try:
            # Generate a unique ID
            memory_id = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Store in ChromaDB
            self.memory_collection.add(
                documents=[content],
                ids=[memory_id],
                metadatas=[{
                    'timestamp': str(datetime.now()),
                    'uri': post_uri,
                    'type': 'post'
                }]
            )
        except Exception as e:
            self.logger.error(f"Failed to store memory: {e}")

    def get_posting_history(self, limit: int = 10) -> List[Dict]:
        """Retrieve recent posting history"""
        try:
            results = self.memory_collection.query(
                query_texts=[""],
                n_results=limit
            )
            
            history = []
            for i, doc in enumerate(results['documents'][0]):
                history.append({
                    'content': doc,
                    'metadata': results['metadatas'][0][i]
                })
            
            return history
        except Exception as e:
            self.logger.error(f"Failed to retrieve history: {e}")
            return []
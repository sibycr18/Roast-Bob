import logging
from typing import List, Dict
from datetime import datetime
from collections import Counter
import re
import chromadb

class BlueskyTrendResearcher:
    def __init__(self, bluesky_client):
        self.client = bluesky_client
        self.logger = logging.getLogger(__name__)
        
        # Initialize ChromaDB for trend storage
        self.chroma_client = chromadb.Client()
        self.trend_collection = self.chroma_client.get_or_create_collection(
            name="trend_history"
        )
        
        self.trend_cache = {
            'trends': [],
            'last_updated': None
        }

    def research_trends(self) -> Dict:
        """Research current trends from feed"""
        try:
            feed_items = self.client.get_feed(limit=100)
            
            # Extract and analyze text content
            texts = [item['text'] for item in feed_items]
            trends = self._analyze_content(texts)
            
            # Store trends in ChromaDB
            self._store_trends(trends)
            
            # Update cache
            self.trend_cache = {
                'trends': trends,
                'last_updated': datetime.now()
            }
            
            return {
                'trends': trends,
                'timestamp': str(datetime.now())
            }
            
        except Exception as e:
            self.logger.error(f"Trend research failed: {e}")
            return {'error': str(e)}

    def _analyze_content(self, texts: List[str]) -> List[Dict]:
        """Analyze texts to identify trends"""
        words = []
        hashtags = []
        topics = []
        
        for text in texts:
            # Extract words and hashtags
            text_words = re.findall(r'\b\w+\b', text.lower())
            text_hashtags = re.findall(r'#(\w+)', text.lower())
            
            # Extract potential topics (capitalized phrases)
            text_topics = re.findall(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', text)
            
            words.extend(text_words)
            hashtags.extend(text_hashtags)
            topics.extend(text_topics)
        
        # Count occurrences
        word_counts = Counter(words)
        hashtag_counts = Counter(hashtags)
        topic_counts = Counter(topics)
        
        # Combine trends
        trends = []
        
        # Add top hashtags
        for tag, count in hashtag_counts.most_common(5):
            trends.append({
                'topic': f'#{tag}',
                'count': count,
                'type': 'hashtag'
            })
        
        # Add top topics
        for topic, count in topic_counts.most_common(5):
            trends.append({
                'topic': topic,
                'count': count,
                'type': 'topic'
            })
        
        # Add top words
        excluded_words = {'https', 'about', 'would', 'their', 'there', 'this', 'that'}
        for word, count in word_counts.most_common(20):
            if len(word) > 4 and word not in excluded_words:
                trends.append({
                    'topic': word,
                    'count': count,
                    'type': 'word'
                })
        
        return sorted(trends, key=lambda x: x['count'], reverse=True)[:10]

    def _store_trends(self, trends: List[Dict]):
        """Store trends in ChromaDB"""
        try:
            timestamp = datetime.now().isoformat()
            
            # Prepare data for storage
            trend_texts = [trend['topic'] for trend in trends]
            trend_metadata = [{
                'count': trend['count'],
                'type': trend['type'],
                'timestamp': timestamp
            } for trend in trends]
            
            # Store in ChromaDB
            self.trend_collection.add(
                documents=trend_texts,
                ids=[f"trend_{timestamp}_{i}" for i in range(len(trends))],
                metadatas=trend_metadata
            )
        except Exception as e:
            self.logger.error(f"Failed to store trends: {e}")

    def get_historical_trends(self, days: int = 7) -> List[Dict]:
        """Retrieve historical trends from ChromaDB"""
        try:
            # Query recent trends
            results = self.trend_collection.query(
                query_texts=[""],
                n_results=50  # Adjust based on needs
            )
            
            # Process and return results
            historical_trends = []
            for i, doc in enumerate(results['documents']):
                historical_trends.append({
                    'topic': doc,
                    'metadata': results['metadatas'][i]
                })
            
            return historical_trends
        except Exception as e:
            self.logger.error(f"Failed to retrieve historical trends: {e}")
            return []
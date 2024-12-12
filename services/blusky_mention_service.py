import logging
from typing import List, Dict, Optional
from datetime import datetime
import chromadb

class BlueskyMentionService:
    def __init__(self, bluesky_client, roast_agent):
        """
        Initialize mention handling service
        
        Args:
            bluesky_client: Authenticated Bluesky client
            roast_agent: Roast generation agent
        """
        self.client = bluesky_client
        self.roast_agent = roast_agent
        self.logger = logging.getLogger(__name__)
        
        # Initialize ChromaDB for mention tracking
        self.chroma_client = chromadb.Client()
        self.mention_collection = self.chroma_client.get_or_create_collection(
            name="mention_history"
        )
        
        # Track processed mentions
        self.processed_mentions = set()

    def handle_mentions(self) -> List[Dict]:
        """
        Process new mentions and generate responses
        
        Returns:
            List of processed mentions with responses
        """
        try:
            # Get recent mentions
            mentions = self.client.get_mentions()
            processed = []
            
            for mention in mentions:
                if self._should_process_mention(mention):
                    response = self._process_mention(mention)
                    if response:
                        processed.append({
                            'mention': mention,
                            'response': response
                        })
                        self._store_mention(mention, response)
            
            return processed
            
        except Exception as e:
            self.logger.error(f"Failed to handle mentions: {e}")
            return []

    def _should_process_mention(self, mention: Dict) -> bool:
        """
        Determine if mention should be processed
        
        Args:
            mention: Mention data
            
        Returns:
            Boolean indicating if mention should be processed
        """
        # Check if already processed
        if mention['uri'] in self.processed_mentions:
            return False
            
        # Check mention timeframe (within last hour)
        mention_time = datetime.fromisoformat(mention['timestamp'].replace('Z', '+00:00'))
        time_diff = datetime.now() - mention_time
        
        if time_diff.total_seconds() > 3600:  # 1 hour
            return False
            
        return True

    def _process_mention(self, mention: Dict) -> Optional[str]:
        """
        Generate response for mention
        
        Args:
            mention: Mention data
            
        Returns:
            Response text or None
        """
        try:
            # Generate roast reply
            response = self.roast_agent.generate_reply(
                tweet=self.roast_agent.Tweet(
                    text=mention['text'],
                    user=mention['author'],
                    timestamp=mention['timestamp']
                )
            )
            
            # Post reply
            post_uri = self.client.post_skeet(
                text=response,
                reply_to=mention['uri']
            )
            
            # Mark as processed
            self.processed_mentions.add(mention['uri'])
            
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to process mention: {e}")
            return None

    def _store_mention(self, mention: Dict, response: str):
        """
        Store mention and response in ChromaDB
        
        Args:
            mention: Mention data
            response: Generated response
        """
        try:
            mention_id = f"mention_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            self.mention_collection.add(
                documents=[f"{mention['text']} || {response}"],
                ids=[mention_id],
                metadatas=[{
                    'author': mention['author'],
                    'timestamp': mention['timestamp'],
                    'uri': mention['uri'],
                    'response_type': 'roast'
                }]
            )
        except Exception as e:
            self.logger.error(f"Failed to store mention: {e}")

    def get_mention_history(self, limit: int = 10) -> List[Dict]:
        """
        Retrieve recent mention history
        
        Args:
            limit: Number of recent mentions to retrieve
            
        Returns:
            List of recent mentions and responses
        """
        try:
            results = self.mention_collection.query(
                query_texts=[""],
                n_results=limit
            )
            
            history = []
            for i, doc in enumerate(results['documents'][0]):
                mention_text, response = doc.split(" || ")
                history.append({
                    'mention': mention_text,
                    'response': response,
                    'metadata': results['metadatas'][0][i]
                })
            
            return history
        except Exception as e:
            self.logger.error(f"Failed to retrieve mention history: {e}")
            return []
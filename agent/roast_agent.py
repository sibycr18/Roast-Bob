from dataclasses import dataclass
from typing import Optional
import random

@dataclass
class Tweet:
    """Represents a post with its metadata."""
    text: str
    user: str
    timestamp: str
    engagement_score: float = 0.0
    sentiment: str = "neutral"

class RoastBobAgent:
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.personality_traits = {
            "savage_level": 0.8,
            "wit_level": 0.7,
            "trend_awareness": 0.9
        }
        
        self.roast_templates = {
            "savage": [
                "Imagine thinking {topic} is your personality trait 💀",
                "Your take on {topic} is so basic, water feels spicy in comparison",
                "Tell me you don't understand {topic} without telling me",
                "This {topic} take is giving 'I just discovered the internet'",
                "POV: You thought your {topic} hot take was revolutionary"
            ],
            "witty": [
                "Approaching {topic} with the confidence of a mediocre tech bro",
                "Your {topic} energy is very 'participation trophy' core",
                "Living proof that you can be passionate about {topic} without understanding it",
                "Plot twist: {topic} isn't your strong suit",
                "Breaking: Local user discovers {topic}, misses point entirely"
            ],
            "trend_aware": [
                "Oh great, another {topic} expert just dropped their groundbreaking study 🔬",
                "Loading {topic} understanding... still at 0%",
                "Welcome to '{topic} Takes That Nobody Asked For'",
                "Currently accepting applications for better {topic} opinions",
                "This {topic} discourse is giving very 2019 energy"
            ]
        }

    def generate_reply(self, tweet: Tweet, style: str = "savage") -> str:
        """Generate a roast reply based on tweet content."""
        topic = self._extract_topic(tweet.text)
        
        # Choose roast style based on content and personality
        if style not in self.roast_templates:
            style = "savage"
            
        templates = self.roast_templates[style]
        roast = random.choice(templates).format(topic=topic)
        
        if self.debug:
            print(f"Generated roast: {roast}")
            
        return roast

    def _extract_topic(self, text: str) -> str:
        """Extract main topic from text."""
        # Simple implementation - use first meaningful word
        words = text.split()
        if words:
            return words[0] if len(words[0]) > 3 else "this"
        return "this"
import os
from dotenv import load_dotenv
from atproto import Client
import json

# Load environment variables from .env file
load_dotenv()

class BlueskySocialClient:
    def __init__(self, handle: str, password: str):
        """
        Initialize Bluesky client with authentication
        
        :param handle: Bluesky user handle
        :param password: User account password
        """
        self.client = Client()
        self.client.login(handle, password)
        print(f"Successfully logged in as {handle}")

    def post_skeet(self, text: str, reply_to: str = None):
        """
        Post a skeet, optionally as a reply
        
        :param text: Content of the skeet
        :param reply_to: URI of the parent post to reply to (optional)
        """
        if reply_to:
            post = self.client.send_post(text=text, reply_to=reply_to)
            print(f"Posted reply: {text}")
            print(f"Reply URI: {post.uri}")
        else:
            post = self.client.send_post(text=text)
            print(f"Posted skeet: {text}")
            print(f"Skeet URI: {post.uri}")

    def get_mentions(self, limit: int = 20):
        """
        Retrieve user mentions
        
        :param limit: Number of mentions to retrieve
        :return: List of mentions
        """
        mentions = self.client.app.bsky.notification.list_notifications(
            # limit=limit
            # filter=['mention']
        )
        
        print("Recent Mentions:")
        for mention in mentions.notifications:
            if mention.reason == 'mention':
                print(f"From: {mention.author.handle}")
                print(f"Text: {mention.record.text}")
                print(f"Created at: {mention.indexed_at}")
                print("---")
        
        return mentions.notifications

    def get_feed(self, limit: int = 20):
        """
        Retrieve user's feed
        
        :param limit: Number of feed items to retrieve
        :return: Feed items
        """
        feed = self.client.app.bsky.feed.get_timeline(
            # limit=limit
        )
        
        print("Recent Feed Items:")
        for item in feed.feed:
            print(f"Author: {item.post.author.handle}")
            print(f"Text: {item.post.record.text}")
            print(f"Created at: {item.post.indexed_at}")
            print("---")
        
        return feed.feed

def main():
    # Retrieve credentials from environment variables
    handle = os.getenv('BLUESKY_HANDLE')
    password = os.getenv('BLUESKY_PASSWORD')
    
    if not handle or not password:
        print("Please set BLUESKY_HANDLE and BLUESKY_PASSWORD in .env file")
        return

    try:
        # Initialize the client
        client = BlueskySocialClient(handle, password)
        
        # # Demonstrate posting a skeet
        # print("\n--- Posting a Skeet ---")
        # client.post_skeet("Hello, Bluesky!")
        
        # Demonstrate getting mentions
        print("\n--- Retrieving Mentions ---")
        client.get_mentions()
        
        # Demonstrate getting feed
        print("\n--- Retrieving Feed ---")
        client.get_feed()
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
import tweepy
import json
import os
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Twitter API credentials
CLIENT_ID = os.getenv('TWITTER_CLIENT_ID')
CLIENT_SECRET = os.getenv('TWITTER_CLIENT_SECRET')
BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
USERNAME = os.getenv('TWITTER_USERNAME')  # Your Twitter username without '@'

def get_user_id(client, username):
    """Get user ID from username"""
    try:
        user = client.get_user(username=username)
        return user.data.id
    except Exception as e:
        print(f"Error getting user ID: {e}")
        return None

def save_mentions(mentions_data, filename='mentions.json'):
    """Save mentions to JSON file"""
    try:
        # Read existing mentions if file exists
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                existing_mentions = json.load(f)
        else:
            existing_mentions = []

        # Add new mentions
        for mention in mentions_data:
            mention_dict = {
                'id': str(mention.id),
                'text': mention.text,
                'created_at': mention.created_at.isoformat() if mention.created_at else None,
                'author_id': str(mention.author_id),
                'saved_at': datetime.now().isoformat()
            }
            
            # Check for duplicates
            if not any(m['id'] == mention_dict['id'] for m in existing_mentions):
                existing_mentions.append(mention_dict)
                print(f"\nNew mention found:")
                print(f"Text: {mention_dict['text']}")
                print(f"Created at: {mention_dict['created_at']}")
                print("-" * 50)

        # Save updated mentions
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(existing_mentions, f, indent=2, ensure_ascii=False)

    except Exception as e:
        print(f"Error saving mentions: {e}")

def check_mentions():
    """Main function to check mentions"""
    try:
        # Initialize client with Bearer Token
        client = tweepy.Client(
            bearer_token=BEARER_TOKEN,
            wait_on_rate_limit=True
        )

        # Get user ID
        user_id = get_user_id(client, USERNAME)
        if not user_id:
            raise Exception("Could not get user ID")

        print(f"Checking mentions for @{USERNAME}")
        
        while True:
            try:
                # Get mentions
                mentions = client.get_users_mentions(
                    id=user_id,
                    tweet_fields=['created_at', 'author_id'],
                    max_results=10
                )

                if mentions.data:
                    save_mentions(mentions.data)
                else:
                    print("No new mentions found")

                # Wait for 5 minutes before next check
                print("\nWaiting 5 minutes before next check...")
                time.sleep(300)

            except Exception as e:
                print(f"Error during mention check: {e}")
                print("Waiting 60 seconds before retry...")
                time.sleep(60)

    except KeyboardInterrupt:
        print("\nStopping mention checker...")
    except Exception as e:
        print(f"Fatal error: {e}")
        print("\nPlease ensure you have:")
        print("1. Created a Twitter Developer Account")
        print("2. Set up a Project in the Twitter Developer Portal")
        print("3. Generated the Bearer Token")
        print("4. Added the correct credentials to your .env file")

def main():
    """Entry point"""
    if not all([BEARER_TOKEN, USERNAME]):
        print("Error: Missing required environment variables.")
        print("Please check your .env file contains:")
        print("TWITTER_BEARER_TOKEN=your_bearer_token_here")
        print("TWITTER_USERNAME=your_username_without_@")
        return

    check_mentions()

if __name__ == "__main__":
    main()
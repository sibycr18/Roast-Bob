import tweepy
from dotenv import load_dotenv
import os
from utils.logger import log_info, log_error

load_dotenv()

# Access Twitter API keys from environment variables
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_KEY_SECRET = os.getenv("TWITTER_API_KEY_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")


def create_twitter_client():
    """
    Creates and returns a Tweepy API client using the credentials.
    """
    try:
        # Authenticate to the Twitter API
        auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_KEY_SECRET)
        auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)

        # Create Tweepy API client
        api = tweepy.API(auth)
        log_info("Twitter client successfully created")
        return api
    except Exception as e:
        log_error(f"Error creating Twitter client: {e}")
        raise Exception("Failed to authenticate with Twitter API")

def get_mentions(api):
    """
    Fetches recent mentions (tweets that tag the bot).

    Args:
        api (tweepy.API): The Tweepy API client.

    Returns:
        list: A list of mention tweets.
    """
    try:
        # Fetch mentions
        mentions = api.mentions_timeline(count=10)
        log_info(f"Fetched {len(mentions)} mentions from Twitter")
        return mentions
    except Exception as e:
        log_error(f"Error fetching mentions: {e}")
        raise Exception("Failed to fetch mentions from Twitter")

def reply_to_mention(api, mention, roast):
    """
    Replies to a tweet mentioning the bot with a roast.

    Args:
        api (tweepy.API): The Tweepy API client.
        mention (tweepy.Status): The tweet mentioning the bot.
        roast (str): The roast message to send as a reply.
    """
    try:
        # Reply to the mention
        api.update_status(
            status=roast,
            in_reply_to_status_id=mention.id
        )
        log_info(f"Replied to mention {mention.id} with roast: {roast}")
    except Exception as e:
        log_error(f"Error replying to mention {mention.id}: {e}")
        raise Exception("Failed to reply to mention")


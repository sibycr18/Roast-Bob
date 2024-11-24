import tweepy
import os, dotenv

# Load environment variables from .env file
dotenv.load_dotenv()

TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# Authenticate using the Bearer Token (Twitter API v2)
client = tweepy.Client(
    bearer_token=TWITTER_BEARER_TOKEN,
    consumer_key=TWITTER_API_KEY,
    consumer_secret=TWITTER_API_SECRET,
    access_token=TWITTER_ACCESS_TOKEN,
    access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
)

# The tweet ID you want to reply to
tweet_id = '1860602963896762545'  # Replace with the actual tweet ID

# Your reply message
reply_message = "This is a reply to the tweet!"

# Reply to the tweet using the API v2 (create_tweet method)
try:
    response = client.create_tweet(text=reply_message, in_reply_to_tweet_id=tweet_id)
    print(f"Reply sent successfully! Tweet ID: {response.data['id']}")
except Exception as e:
    print(f"Error: {e}")

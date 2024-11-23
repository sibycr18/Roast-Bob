from fastapi import FastAPI
from utils.twitter import create_twitter_client, get_mentions, reply_to_mention
from utils.together_ai import generate_roast
from utils.logger import log_info, log_error

# Initialize FastAPI app
app = FastAPI()

# Initialize Twitter client
api = create_twitter_client()

@app.on_event("startup")
async def on_startup():
    """
    This will run when the FastAPI app starts.
    It fetches mentions from Twitter and replies with roasts.
    """
    try:
        # Fetch mentions from Twitter
        mentions = get_mentions(api)
        
        for mention in mentions:
            # For each mention, roast it in a random style
            roast = generate_roast("Shakespeare", mention.text)  # You can use other styles too.
            
            # Reply to the mention with the generated roast
            reply_to_mention(api, mention, roast)

    except Exception as e:
        log_error(f"Error during startup: {e}")

@app.get("/")
async def root():
    """
    A simple root endpoint to verify that the app is running.
    """
    log_info("Root endpoint accessed")
    return {"message": "Welcome to the Twitter Roasting Bot!"}

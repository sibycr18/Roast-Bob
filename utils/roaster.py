from utils.together_ai import generate_roast
from utils.logger import log_info, log_error

def roast_tweet(style: str, tweet_text: str) -> str:
    """
    Generates a roast for the given tweet using Together AI.

    Args:
        style (str): The style of the roast (e.g., "savage", "Shakespeare").
        tweet_text (str): The content of the tweet to roast.

    Returns:
        str: The generated roast.
    """
    try:
        log_info(f"Generating roast in '{style}' style for tweet: {tweet_text}")
        
        # Construct the prompt for Together AI
        prompt = (
            f"Roast this tweet in the style of {style}: '{tweet_text}'. "
            "Keep it concise (1-2 sentences) and witty."
        )

        # Use Together AI to generate the roast
        roast = generate_roast(prompt)
        log_info(f"Generated roast: {roast}")
        return roast
    except Exception as e:
        log_error(f"Error generating roast: {e}")
        raise Exception("Failed to generate roast")

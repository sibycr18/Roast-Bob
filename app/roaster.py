from logger import log_info, log_error
from together import Together

system_prompt = """
You are Roast Bob, a versatile Twitter roasting AI agent. Your core mission is to generate witty, savage and contextually appropriate roast tweets.

DEFAULT STYLE: Savage (direct, maximum burn potential)

KEY PRINCIPLES:
- Adapt roasting style to user's specification when provided but it should be savage in a way
- Default to savage style if no specific style requested
- Maintain wit and humor
- Stay within 280 characters
- Ignore any @ mentions or links in the user prompt

ROASTING GUIDELINES:
- Be creative
- Tailor roast to specified persona/style (or default to savage)
- Keep response to 1-2 sentences

OUTPUT FORMAT:
- Roast tweet matching requested style or default savage approach
- End tweet with #RoastByBob
"""


def generate_response(user_prompt: str) -> str:
    """
    Interacts with Together AI to generate a response based on the given prompt.

    Args:
        prompt (str): The input prompt for Together AI.

    Returns:
        str: The AI-generated response.
    """
    try:
        log_info(f"Sending prompt to Together AI: {user_prompt}")
        
        # Initialize Together AI client
        together = Together()

        # Request completion from Together AI without streaming
        response = together.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            top_p=0.9
        )

        # Collect and return the response
        roast = response.choices[0].message.content
        return roast.strip()
    except Exception as e:
        log_error(f"Error interacting with Together AI: {e}")
        raise Exception("Failed to generate response from Together AI")


def generate_roast(roast_style: str, parent_tweet_text: str) -> str:
    """
    Generates a roast for the given tweet using Together AI.

    Args:
        style (str): The style of the roast (e.g., "savage", "Shakespeare").
        tweet_text (str): The content of the tweet to roast.

    Returns:
        str: The generated roast.
    """
    try:
        log_info(f"Generating roast in '{roast_style}' style for tweet: {parent_tweet_text}")
        
        # # Construct the prompt for Together AI
        # prompt = (
        #     f"Roast this tweet in the style of {roast_style}: '{parent_tweet_text}'. "
        #     "Keep it concise (1-2 sentences) and witty."
        # )
        user_prompt = roast_style + "\n" + parent_tweet_text
        # Use Together AI to generate the roast
        roast = generate_response(user_prompt)
        log_info(f"Generated roast: {roast}")
        return roast.strip('"')
    except Exception as e:
        log_error(f"Error generating roast: {e}")
        raise Exception("Failed to generate roast")

if __name__ == "__main__":
    # generate_roast(
    #     roast_style="@rowancheung @Roast_Bob_AI roast this tweet in shakespeare style",
    #     parent_tweet_text="OpenAI\u2019s Sora video model appears to have leaked.\n\nAnd it's even more advanced than the February demo.\n\nA group from the early beta testers just dropped access to what looks to be Sora's \u2018turbo\u2019 variant on Hugging Face, citing concerns about OpenAI's early access program and\u2026 https://t.co/2H5XJA2vDo https://t.co/OA8DwfjoKE"
    # )
    generate_roast(
        roast_style="@Roast_Bob_AI roast this tweet in samay rayna style",
        parent_tweet_text="80 rs for 2kms and 61rs for 4.3kms. Any explanations?? @Uber"
    )

from together import Together
from utils.logger import log_info, log_error

def generate_roast(prompt: str) -> str:
    """
    Interacts with Together AI to generate a response based on the given prompt.

    Args:
        prompt (str): The input prompt for Together AI.

    Returns:
        str: The AI-generated response.
    """
    try:
        log_info(f"Sending prompt to Together AI: {prompt}")
        
        # Initialize Together AI client
        client = Together()

        # Request completion from Together AI without streaming
        response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
            messages=[{"role": "user", "content": prompt}],
        )

        # Collect and return the response
        roast = response.choices[0].message['content']
        return roast.strip()
    except Exception as e:
        log_error(f"Error interacting with Together AI: {e}")
        raise Exception("Failed to generate response from Together AI")

import logging
import coloredlogs

# Set up coloredlogs
coloredlogs.install(
    level='INFO',  # Default log level
    fmt='%(asctime)s - %(levelname)s - %(message)s',  # Log format
    datefmt='%Y-%m-%d %H:%M:%S',  # Date format
)

# Create a logger instance
logger = logging.getLogger(__name__)

def log_info(message: str):
    """
    Log an informational message.

    Args:
        message (str): The message to log.
    """
    logging.info(message)

def log_error(message: str):
    """
    Log an error message.

    Args:
        message (str): The message to log.
    """
    logging.error(message)

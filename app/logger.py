# In logger.py
import logging
import coloredlogs
import os
from logging.handlers import RotatingFileHandler

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Custom color scheme (keep existing)
CUSTOM_LEVEL_STYLES = {
    'info': {'color': 'green', 'bold': True},
    'warning': {'color': 'yellow', 'bold': True},
    'error': {'color': 'red', 'bold': True, 'background': 'black'},
    'critical': {'color': 'red', 'bold': True, 'background': 'black', 'decoration': 'blink'},
    'debug': {'color': 'blue', 'bold': True}
}

CUSTOM_FIELD_STYLES = {
    'asctime': {'color': 'magenta'},
    'hostname': {'color': 'magenta'},
    'levelname': {'color': 'cyan', 'bold': True},
    'name': {'color': 'blue'},
    'programname': {'color': 'cyan'}
}

def setup_logger(service_name: str):
    """
    Set up a logger for a specific service with both console and file logging.
    
    Args:
        service_name (str): Name of the service
    
    Returns:
        logging.Logger: Configured logger
    """
    # Create logger
    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)
    
    # Clear any existing handlers to prevent duplicate logs
    logger.handlers.clear()
    
    # Console handler with colored logs
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler with rotating logs
    file_handler = RotatingFileHandler(
        f'logs/{service_name}.log', 
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # Add both handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # Apply colored formatting to console
    coloredlogs.install(
        level='INFO',
        logger=logger,
        fmt='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level_styles=CUSTOM_LEVEL_STYLES,
        field_styles=CUSTOM_FIELD_STYLES
    )
    
    return logger

# Replace existing logging functions
def log_info(message: str, logger=None):
    """
    Log an informational message.

    Args:
        message (str): The message to log.
        logger (logging.Logger, optional): Specific logger to use.
    """
    if logger:
        logger.info(message)
    else:
        logging.info(message)

def log_error(message: str, logger=None):
    """
    Log an error message.

    Args:
        message (str): The message to log.
        logger (logging.Logger, optional): Specific logger to use.
    """
    if logger:
        logger.error(message)
    else:
        logging.error(message)

coloredlogs.install(
    level='INFO',
    fmt='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level_styles=CUSTOM_LEVEL_STYLES,
    field_styles=CUSTOM_FIELD_STYLES
)

logging.getLogger().setLevel(logging.INFO)  # Set root logger level
logging.basicConfig(level=logging.INFO)
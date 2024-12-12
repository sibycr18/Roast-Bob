import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
from typing import Optional
from datetime import datetime

class LoggerSetup:
    """
    Utility class for setting up consistent logging across services
    """
    def __init__(self):
        self.log_dir = Path(__file__).parent.parent / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # Default format
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def get_logger(
        self,
        name: str,
        log_file: Optional[str] = None,
        level: int = logging.INFO,
        max_bytes: int = 5_242_880,  # 5MB
        backup_count: int = 3
    ) -> logging.Logger:
        """
        Get a configured logger instance
        
        Args:
            name: Logger name (usually __name__)
            log_file: Specific log file name (defaults to name.log)
            level: Logging level
            max_bytes: Maximum size of log file before rotation
            backup_count: Number of backup files to keep
            
        Returns:
            Configured logger instance
        """
        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # Clear any existing handlers
        logger.handlers = []
        
        # Determine log file name
        if not log_file:
            log_file = f"{name.split('.')[-1]}.log"
        
        # Create file handler
        file_handler = RotatingFileHandler(
            self.log_dir / log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setFormatter(self.formatter)
        logger.addHandler(file_handler)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self.formatter)
        logger.addHandler(console_handler)
        
        return logger

    def get_service_logger(
        self,
        service_name: str,
        include_timestamp: bool = False
    ) -> logging.Logger:
        """
        Get a logger specifically configured for a service
        
        Args:
            service_name: Name of the service
            include_timestamp: Whether to include timestamp in log file name
            
        Returns:
            Configured logger instance
        """
        if include_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d")
            log_file = f"{service_name}_{timestamp}.log"
        else:
            log_file = f"{service_name}.log"
        
        return self.get_logger(
            name=f"service.{service_name}",
            log_file=log_file,
            level=logging.INFO
        )

# Create a global instance
logger_setup = LoggerSetup()

def get_logger(name: str) -> logging.Logger:
    """
    Convenience function to get a logger
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logger_setup.get_logger(name)

def get_service_logger(service_name: str) -> logging.Logger:
    """
    Convenience function to get a service logger
    
    Args:
        service_name: Name of the service
        
    Returns:
        Configured logger instance
    """
    return logger_setup.get_service_logger(service_name)

# Example usage in other files:
"""
from utils.logger import get_logger
logger = get_logger(__name__)

# Or for services:
from utils.logger import get_service_logger
logger = get_service_logger('mention_service')
"""
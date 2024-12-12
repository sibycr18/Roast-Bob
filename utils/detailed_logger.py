import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import os
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime
import json
import traceback

class DetailedLogger:
    """Enhanced logging utility with detailed tracking"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Create separate log files for different severity levels
        self.setup_file_loggers()

    def setup_file_loggers(self):
        """Setup different log files for various logging levels"""
        # Main detailed log
        detailed_handler = RotatingFileHandler(
            self.log_dir / f"{self.service_name}_detailed.log",
            maxBytes=10_485_760,  # 10MB
            backupCount=5
        )
        detailed_handler.setLevel(logging.DEBUG)
        
        # Error log
        error_handler = RotatingFileHandler(
            self.log_dir / f"{self.service_name}_error.log",
            maxBytes=5_242_880,  # 5MB
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        
        # Console output
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - [%(levelname)s] - '
            '%(funcName)s:%(lineno)d - %(message)s'
        )
        
        # Apply formatters
        detailed_handler.setFormatter(detailed_formatter)
        error_handler.setFormatter(detailed_formatter)
        console_handler.setFormatter(detailed_formatter)
        
        # Setup logger
        self.logger = logging.getLogger(self.service_name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(detailed_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(console_handler)

    def debug(self, msg: str, **kwargs):
        """Log debug message with additional context"""
        context = json.dumps(kwargs) if kwargs else ""
        self.logger.debug(f"{msg} {context}")

    def info(self, msg: str, **kwargs):
        """Log info message with additional context"""
        context = json.dumps(kwargs) if kwargs else ""
        self.logger.info(f"{msg} {context}")

    def error(self, msg: str, error: Exception = None, **kwargs):
        """Log error message with exception details and context"""
        error_details = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            **kwargs
        } if error else kwargs
        
        self.logger.error(f"{msg} {json.dumps(error_details, indent=2)}")

# Create logger instances for different services
mention_logger = DetailedLogger("mention_service")
content_logger = DetailedLogger("content_service")
trend_logger = DetailedLogger("trend_service")
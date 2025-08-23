# src/utils/logger.py - Updated version
import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler

def setup_logging(log_file: str = "logs/app.log", level: str = "INFO",
                 max_bytes: int = 10*1024*1024, backup_count: int = 5):
    """Setup application logging with configurable parameters"""

    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Get log level
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count
            ),
            logging.StreamHandler()  # Also log to console
        ]
    )

    # Set specific levels for noisy modules
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)

    return logging.getLogger(__name__)
"""
Advanced Biometric Application - Main Package
This package contains the core functionality for biometric device management and attendance tracking.
"""

__version__ = "1.0.0"
__author__ = "Advanced Biometric Application Team"

# Import key modules for easier access
from src.core import device_manager, attendance_service, database
from src.utils import config_manager, logger, windows_utils
from src.biometric import zk_device

# Package-level initialization
def initialize_application():
    """
    Initialize the application components
    """
    # Initialize configuration
    config = config_manager.ConfigManager()

    # Initialize logger
    app_logger = logger.setup_logger()

    app_logger.info("Application package initialized")
    return config

# Export main components for easy access
__all__ = [
    'device_manager',
    'attendance_service',
    'database',
    'config_manager',
    'logger',
    'windows_utils',
    'zk_device',
    'initialize_application'
]
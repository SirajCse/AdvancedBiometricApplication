"""
Biometric Device Integration Package
This package provides interfaces for ZKTeco biometric device communication and management.
"""

from .zk_device import ZKDevice
from .zk_lib import (
    attendance as zk_attendance,
    base as zk_base,
    const as zk_const,
    exception as zk_exception,
    finger as zk_finger,
    user as zk_user
)

# Version information
__version__ = "1.0.0"
__author__ = "Biometric Integration Team"

# Export main classes and modules
__all__ = [
    'ZKDevice',
    'zk_attendance',
    'zk_base',
    'zk_const',
    'zk_exception',
    'zk_finger',
    'zk_user'
]

# Package initialization
def initialize_biometric_module():
    """
    Initialize the biometric module components
    """
    print("Biometric module initialized")
    # Additional initialization code can be added here

# Create aliases for common imports
ZKAttendance = zk_attendance
ZKBase = zk_base
ZKConstants = zk_const
ZKException = zk_exception
ZKFinger = zk_finger
ZKUser = zk_user
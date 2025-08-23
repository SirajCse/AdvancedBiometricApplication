# src/utils/windows_utils.py (Enhanced)
import os
import sys
import winreg
import logging
import subprocess
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)

class WindowsStartupManager:
    # ... (previous code remains the same) ...

    @staticmethod
    def protect_executable(exe_path: str):
        """Apply protection measures to executable"""
        try:
            # 1. Set file permissions to restrict access
            subprocess.run([
                'icacls', exe_path,
                '/inheritance:r',
                '/grant:r', 'Administrators:(F)',
                '/grant:r', 'SYSTEM:(F)',
                '/grant:r', 'Users:(RX)'
            ], check=True)

            # 2. Mark as critical system file (Windows only)
            try:
                subprocess.run([
                    'attrib', '+S', '+H', '+R', exe_path
                ], check=True)
            except:
                pass  # This might not work on all systems

            logger.info(f"Applied protection to {exe_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to protect executable: {e}")
            return False

    @staticmethod
    def verify_executable_integrity(exe_path: str) -> bool:
        """Verify executable hasn't been tampered with"""
        try:
            # Calculate current hash
            with open(exe_path, 'rb') as f:
                current_hash = hashlib.sha256(f.read()).hexdigest()

            # Compare with expected hash (would be stored securely)
            expected_hash = WindowsStartupManager.get_expected_hash()

            if expected_hash and current_hash != expected_hash:
                logger.warning("Executable integrity check failed!")
                return False

            return True

        except Exception as e:
            logger.error(f"Integrity check failed: {e}")
            return False

    @staticmethod
    def get_expected_hash():
        """Get expected hash (in real implementation, store this securely)"""
        # In production, this should be stored encrypted or in a secure location
        return None  # Replace with actual hash
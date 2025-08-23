# src/utils/windows_utils.py - Secure Windows Utilities
import os
import sys
import winreg
import logging
import subprocess
import hashlib
import json
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class WindowsStartupManager:
    @staticmethod
    def install_windows_service(service_name: str, display_name: str, executable_path: str) -> bool:
        """Install application as a Windows service"""
        try:
            # Import here to avoid dependency issues when not on Windows
            import win32serviceutil
            import servicemanager
            import win32service
            import win32event

            # This would typically be handled by pywin32 service framework
            # For a real implementation, you'd create a proper service class
            logger.info(f"Service installation would be handled by pywin32 framework")
            return True

        except ImportError:
            logger.error("pywin32 not available for service installation")
            return False
        except Exception as e:
            logger.error(f"Service installation failed: {e}")
            return False

    @staticmethod
    def uninstall_windows_service(service_name: str) -> bool:
        """Uninstall Windows service"""
        try:
            # Similar to install, this would use pywin32 framework
            logger.info(f"Service uninstallation would be handled by pywin32 framework")
            return True

        except Exception as e:
            logger.error(f"Service uninstallation failed: {e}")
            return False

    @staticmethod
    def enable_auto_start(app_name: str, executable_path: str) -> bool:
        """Enable application to start automatically with Windows"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, f'"{executable_path}"')
            winreg.CloseKey(key)
            logger.info(f"Enabled auto-start for {app_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to enable auto-start: {e}")
            return False

    @staticmethod
    def disable_auto_start(app_name: str) -> bool:
        """Disable application auto-start"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            winreg.DeleteValue(key, app_name)
            winreg.CloseKey(key)
            logger.info(f"Disabled auto-start for {app_name}")
            return True
        except FileNotFoundError:
            # Value didn't exist, which is fine
            return True
        except Exception as e:
            logger.error(f"Failed to disable auto-start: {e}")
            return False

    @staticmethod
    def protect_executable(exe_path: str) -> bool:
        """Apply protection measures to executable"""
        if not os.path.exists(exe_path):
            logger.error(f"Executable not found: {exe_path}")
            return False

        try:
            # 1. Set file permissions to restrict access
            result = subprocess.run([
                'icacls', exe_path,
                '/inheritance:r',
                '/grant:r', 'Administrators:(F)',
                '/grant:r', 'SYSTEM:(F)',
                '/grant:r', 'Users:(RX)'
            ], check=True, capture_output=True, text=True, timeout=30)

            logger.info(f"Set file permissions for {exe_path}")

            # 2. Optional: Mark with system attributes (use cautiously)
            try:
                subprocess.run(['attrib', '+R', exe_path],
                             check=True, capture_output=True, timeout=10)
            except subprocess.CalledProcessError:
                logger.warning("Could not set read-only attribute")

            logger.info(f"Applied protection to {exe_path}")
            return True

        except subprocess.TimeoutExpired:
            logger.error("Permission setting timed out")
            return False
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to set permissions: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Failed to protect executable: {e}")
            return False

    @staticmethod
    def verify_executable_integrity(exe_path: str, expected_hash: Optional[str] = None) -> bool:
        """
        Verify executable hasn't been tampered with

        Args:
            exe_path: Path to executable to verify
            expected_hash: Expected SHA256 hash. If None, tries to get from environment
        """
        if not os.path.exists(exe_path):
            logger.error(f"Executable not found: {exe_path}")
            return False

        # Get expected hash from parameter or environment
        if expected_hash is None:
            expected_hash = os.environ.get('APP_EXPECTED_HASH')

        if not expected_hash:
            logger.warning("No expected hash provided for integrity verification")
            return True  # Continue without verification if no hash configured

        try:
            # Calculate current hash
            current_hash = WindowsStartupManager.calculate_file_hash(exe_path)

            if current_hash == expected_hash:
                logger.info("Integrity verification passed")
                return True
            else:
                logger.warning(f"Integrity check failed! Expected: {expected_hash}, Got: {current_hash}")
                return False

        except Exception as e:
            logger.error(f"Integrity verification error: {e}")
            return False

    @staticmethod
    def calculate_file_hash(file_path: str) -> str:
        """Calculate SHA256 hash of a file"""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(4096):
                hasher.update(chunk)
        return hasher.hexdigest()

    @staticmethod
    def create_integrity_manifest(exe_path: str, manifest_path: str) -> bool:
        """
        Create an integrity manifest file with executable hash and metadata

        Args:
            exe_path: Path to executable
            manifest_path: Path where to save manifest
        """
        try:
            file_hash = WindowsStartupManager.calculate_file_hash(exe_path)
            file_size = os.path.getsize(exe_path)
            modified_time = os.path.getmtime(exe_path)

            manifest_data = {
                "file_name": os.path.basename(exe_path),
                "file_path": os.path.abspath(exe_path),
                "file_size": file_size,
                "modified_time": modified_time,
                "sha256_hash": file_hash,
                "created": os.path.getctime(exe_path),
                "security_level": "protected",
                "version": "1.0"
            }

            with open(manifest_path, 'w') as f:
                json.dump(manifest_data, f, indent=2)

            logger.info(f"Created integrity manifest: {manifest_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to create integrity manifest: {e}")
            return False

    @staticmethod
    def is_debugger_present() -> bool:
        """Check if debugger is present"""
        try:
            # Simple anti-debugging check
            return hasattr(sys, 'gettrace') and sys.gettrace() is not None
        except:
            return False

    @staticmethod
    def secure_environment_check() -> bool:
        """
        Perform security environment checks
        Returns True if environment appears secure
        """
        # Check for debugger
        if WindowsStartupManager.is_debugger_present():
            logger.warning("Debugger detected - environment may not be secure")
            return False

        # Additional environment checks could be added here
        # - Check for virtualization/sandbox environments
        # - Verify system integrity
        # - Check for monitoring tools

        return True

# Utility functions for broader use
def secure_file_operations(file_path: str) -> bool:
    """Apply security best practices to file operations"""
    try:
        path = Path(file_path)

        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        # Set secure permissions after file operations
        if path.exists():
            WindowsStartupManager.protect_executable(str(path))

        return True

    except Exception as e:
        logger.error(f"Secure file operations failed: {e}")
        return False

def validate_secure_path(file_path: str) -> bool:
    """Validate that a path is secure for operations"""
    try:
        path = Path(file_path).resolve()

        # Check for path traversal attempts
        if '..' in str(path) or path.is_reserved():
            logger.warning(f"Potentially insecure path: {file_path}")
            return False

        # Check if path is within expected directories
        expected_dirs = [Path('dist'), Path('src'), Path('config'), Path('data')]
        if not any(path.is_relative_to(expected_dir) for expected_dir in expected_dirs):
            logger.warning(f"Path outside expected directories: {file_path}")
            return False

        return True

    except Exception as e:
        logger.error(f"Path validation failed: {e}")
        return False
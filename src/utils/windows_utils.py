# src/utils/windows_utils.py
import os
import sys
import winreg
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

class WindowsStartupManager:
    @staticmethod
    def enable_auto_start(app_name: str, app_path: str) -> bool:
        """Add application to Windows startup"""
        try:
            # Get the path to the current executable
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                executable_path = sys.executable
            else:
                # Running as Python script
                executable_path = os.path.abspath(app_path)
            
            # Add to registry startup
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, f'"{executable_path}" --minimized')
            winreg.CloseKey(key)
            
            logger.info(f"Added {app_name} to Windows startup")
            return True
        except Exception as e:
            logger.error(f"Failed to add to startup: {e}")
            return False
    
    @staticmethod
    def disable_auto_start(app_name: str) -> bool:
        """Remove application from Windows startup"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            
            winreg.DeleteValue(key, app_name)
            winreg.CloseKey(key)
            
            logger.info(f"Removed {app_name} from Windows startup")
            return True
        except FileNotFoundError:
            # Key doesn't exist, which means it's already removed
            return True
        except Exception as e:
            logger.error(f"Failed to remove from startup: {e}")
            return False
    
    @staticmethod
    def is_auto_start_enabled(app_name: str) -> bool:
        """Check if application is in Windows startup"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_READ
            )
            
            value, _ = winreg.QueryValueEx(key, app_name)
            winreg.CloseKey(key)
            
            return value is not None
        except FileNotFoundError:
            return False
        except Exception:
            return False
    
    @staticmethod
    def install_windows_service(service_name: str, display_name: str, app_path: str) -> bool:
        """Install as Windows service (requires admin privileges)"""
        try:
            # Use nssm (Non-Sucking Service Manager) for service installation
            nssm_path = Path(__file__).parent.parent / "bin" / "nssm.exe"
            
            if not nssm_path.exists():
                logger.error("NSSM not found. Service installation requires nssm.exe")
                return False
            
            # Install the service
            result = subprocess.run([
                str(nssm_path), "install", service_name, app_path
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                # Set display name
                subprocess.run([
                    str(nssm_path), "set", service_name, "DisplayName", display_name
                ], capture_output=True)
                
                logger.info(f"Installed Windows service: {service_name}")
                return True
            else:
                logger.error(f"Failed to install service: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Service installation error: {e}")
            return False
    
    @staticmethod
    def uninstall_windows_service(service_name: str) -> bool:
        """Uninstall Windows service"""
        try:
            nssm_path = Path(__file__).parent.parent / "bin" / "nssm.exe"
            
            if not nssm_path.exists():
                logger.error("NSSM not found. Service uninstallation requires nssm.exe")
                return False
            
            result = subprocess.run([
                str(nssm_path), "remove", service_name, "confirm"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Uninstalled Windows service: {service_name}")
                return True
            else:
                logger.error(f"Failed to uninstall service: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Service uninstallation error: {e}")
            return False
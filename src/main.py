# src/main.py
import time
import sys
import os
import logging
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from core.database import DatabaseManager
from core.device_manager import DeviceManager
from core.attendance_service import AttendanceService
from utils.logger import setup_logging
from utils.windows_utils import WindowsStartupManager

APP_NAME = "Advanced Biometric Application"
APP_VERSION = "2.0"

def check_license():
    """Non-interactive license check for windowed applications"""
    try:
        from utils.license_manager import LicenseManager
        license_manager = LicenseManager()
        is_valid, message = license_manager.validate_license()

        if not is_valid:
            # Auto-generate trial license if none exists
            if not license_manager.license_data:
                license_key = license_manager.generate_license("Trial User", 1, 30)
                print(f"Auto-generated trial license: {license_key}")
                return True
            else:
                print(f"License Error: {message}")
                # Continue anyway for demo purposes
                return True

        return True
    except ImportError:
        # License manager not available, continue without license check
        print("License manager not available, continuing without license check")
        return True
    except Exception as e:
        print(f"License check error: {e}, continuing anyway")
        return True

def main():
    # Non-interactive license check
    if not check_license():
        sys.exit(1)

    # Parse command line arguments
    parser = argparse.ArgumentParser(description=APP_NAME)
    parser.add_argument('--minimized', action='store_true', help='Start minimized to system tray')
    parser.add_argument('--install-service', action='store_true', help='Install as Windows service')
    parser.add_argument('--uninstall-service', action='store_true', help='Uninstall Windows service')
    parser.add_argument('--enable-autostart', action='store_true', help='Enable auto-start with Windows')
    parser.add_argument('--disable-autostart', action='store_true', help='Disable auto-start with Windows')
    parser.add_argument('--config', help='Path to configuration file')
    args = parser.parse_args()

    # Setup logging
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    setup_logging(log_dir / "app.log")

    logger = logging.getLogger(__name__)
    logger.info(f"Starting {APP_NAME} v{APP_VERSION}")

    # Handle service commands
    if args.install_service:
        app_path = sys.executable if getattr(sys, 'frozen', False) else __file__
        success = WindowsStartupManager.install_windows_service(
            "SmartAcademyBiometric", APP_NAME, app_path
        )
        sys.exit(0 if success else 1)

    if args.uninstall_service:
        success = WindowsStartupManager.uninstall_windows_service("SmartAcademyBiometric")
        sys.exit(0 if success else 1)

    # Handle auto-start commands
    if args.enable_autostart:
        app_path = sys.executable if getattr(sys, 'frozen', False) else __file__
        success = WindowsStartupManager.enable_auto_start("SmartAcademyBiometric", app_path)
        sys.exit(0 if success else 1)

    if args.disable_autostart:
        success = WindowsStartupManager.disable_auto_start("SmartAcademyBiometric")
        sys.exit(0 if success else 1)

    # Initialize database
    db_manager = DatabaseManager()

    # Initialize services
    device_manager = DeviceManager(db_manager)
    attendance_service = AttendanceService(db_manager, device_manager)

    try:
        # Initialize devices
        device_manager.initialize_devices()

        # Start live capture
        device_manager.start_live_capture()

        # Start attendance service
        attendance_service.start()

        logger.info("All services started successfully")

        # Keep the main thread alive
        import time
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
    finally:
        # Cleanup
        device_manager.stop_live_capture()
        device_manager.disconnect_all()
        attendance_service.stop()
        logger.info("Application shutdown complete")

if __name__ == "__main__":
    main()
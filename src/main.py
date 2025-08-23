# src/main.py
import sys
import os
import logging
import argparse
from pathlib import Path

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import DatabaseManager
from core.device_manager import DeviceManager
from core.attendance_service import AttendanceService
from utils.logger import setup_logging
from utils.windows_utils import WindowsStartupManager
from utils.config_manager import ConfigManager

APP_NAME = "Advanced Biometric Application"
APP_VERSION = "2.0"

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description=APP_NAME)
    parser.add_argument('--minimized', action='store_true', help='Start minimized')
    parser.add_argument('--install-service', action='store_true', help='Install as Windows service')
    parser.add_argument('--uninstall-service', action='store_true', help='Uninstall Windows service')
    parser.add_argument('--enable-autostart', action='store_true', help='Enable auto-start with Windows')
    parser.add_argument('--disable-autostart', action='store_true', help='Disable auto-start with Windows')
    parser.add_argument('--config', help='Path to configuration file')
    args = parser.parse_args()

    # ===== CONFIGURATION LOADING =====
    # Load configuration
    config_manager = ConfigManager()

    # Use custom config file if specified, otherwise default
    config_file = args.config if args.config else "default_config.json"
    config = config_manager.load_config(config_file)

    # Validate configuration - with basic logging for errors
    if not config_manager.validate_config(config):
        # Setup minimal logging for error message
        setup_logging('logs/app.log', 'ERROR')
        logger = logging.getLogger(__name__)
        logger.error("Configuration validation failed! Please check your config file.")
        sys.exit(1)

    # Set encryption key from environment if available
    encryption_key = os.environ.get('CONFIG_ENCRYPTION_KEY')
    if encryption_key:
        config_manager.encryption_key = encryption_key
    # ===== END CONFIGURATION LOADING =====

    # Setup logging - now using config from loaded configuration
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Use config for logging setup
    log_config = config.get('logging', {})
    setup_logging(
        log_file=log_config.get('file', 'logs/app.log'),
        level=log_config.get('level', 'INFO'),
        max_bytes=log_config.get('max_size_mb', 10) * 1024 * 1024,
        backup_count=log_config.get('backup_count', 5)
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
    logger.info(f"Loaded configuration from: {config_file}")

    # Handle service commands
    if args.install_service:
        app_path = sys.executable if getattr(sys, 'frozen', False) else __file__
        success = WindowsStartupManager.install_windows_service(
            "AdvancedBiometric", APP_NAME, app_path
        )
        sys.exit(0 if success else 1)

    if args.uninstall_service:
        success = WindowsStartupManager.uninstall_windows_service("AdvancedBiometric")
        sys.exit(0 if success else 1)

    # Handle auto-start commands
    if args.enable_autostart:
        app_path = sys.executable if getattr(sys, 'frozen', False) else __file__
        success = WindowsStartupManager.enable_auto_start("AdvancedBiometric", app_path)
        sys.exit(0 if success else 1)

    if args.disable_autostart:
        success = WindowsStartupManager.disable_auto_start("AdvancedBiometric")
        sys.exit(0 if success else 1)

    # Initialize database - now using config
    db_config = config.get('database', {})
    db_manager = DatabaseManager(db_path=db_config.get('path', 'data/att.db'))

    # Initialize services - pass config to managers
    device_manager = DeviceManager(db_manager, config)
    attendance_service = AttendanceService(db_manager, device_manager, config)

    try:
        # Initialize devices using config
        devices_config = config.get('devices', [])
        device_manager.initialize_devices(devices_config)

        # Start live capture
        device_manager.start_live_capture()

        # Start attendance service using sync config
        sync_config = config.get('sync', {})
        attendance_service.start(sync_config)

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
# src/utils/config_manager.py
import json
import os
from pathlib import Path
from typing import Dict, Any

class ConfigManager:
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def load_config(self, filename: str = "app_config.json") -> Dict[str, Any]:
        """Load configuration from JSON file"""
        config_path = self.config_dir / filename

        if not config_path.exists():
            return self.create_default_config(config_path)

        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.create_default_config(config_path)

    def create_default_config(self, config_path: Path) -> Dict[str, Any]:
        """Create default configuration file"""
        default_config = {
            "database": {
                "path": "data/att.db",
                "auto_create": True
            },
            "logging": {
                "level": "INFO",
                "file": "logs/app.log",
                "max_size_mb": 10,
                "backup_count": 5
            },
            "sync": {
                "interval_seconds": 300,
                "retry_attempts": 3,
                "retry_delay_seconds": 60
            },
            "devices": {
                "auto_connect": True,
                "connection_timeout": 30,
                "reconnect_interval": 60
            },
            "application": {
                "auto_start": False,
                "minimize_to_tray": True,
                "check_for_updates": True
            }
        }

        try:
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=4)
            print(f"Created default config at {config_path}")
        except Exception as e:
            print(f"Error creating default config: {e}")

        return default_config

    def save_config(self, config: Dict[str, Any], filename: str = "app_config.json"):
        """Save configuration to JSON file"""
        config_path = self.config_dir / filename

        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
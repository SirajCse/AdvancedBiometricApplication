# src/utils/config_manager.py - Enhanced Configuration Manager
import json
import configparser
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
import hashlib

logger = logging.getLogger(__name__)

class ConfigManager:
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.encryption_key = os.environ.get('CONFIG_ENCRYPTION_KEY')

    def load_config(self, filename: str = "app_config.json") -> Dict[str, Any]:
        """Load configuration from JSON or INI file"""
        config_path = self.config_dir / filename

        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}")
            return self.create_default_config(config_path)

        try:
            if filename.endswith('.json'):
                return self._load_json_config(config_path)
            elif filename.endswith('.ini'):
                return self._load_ini_config(config_path)
            else:
                logger.error(f"Unsupported config format: {filename}")
                return self.create_default_config(config_path)

        except Exception as e:
            logger.error(f"Error loading config {filename}: {e}")
            return self.create_default_config(config_path)

    def _load_json_config(self, config_path: Path) -> Dict[str, Any]:
        """Load JSON configuration file"""
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Decrypt sensitive values if encryption is enabled
        if self.encryption_key:
            config = self._decrypt_config_values(config)

        return config

    def _load_ini_config(self, config_path: Path) -> Dict[str, Any]:
        """Load INI configuration file and convert to dictionary"""
        config = configparser.ConfigParser()
        config.read(config_path)

        result = {}
        for section in config.sections():
            result[section] = dict(config.items(section))

        # Decrypt sensitive values if encryption is enabled
        if self.encryption_key:
            result = self._decrypt_config_values(result)

        return result

    def save_config(self, config: Dict[str, Any], filename: str = "app_config.json") -> bool:
        """Save configuration to file"""
        config_path = self.config_dir / filename

        try:
            config_to_save = config.copy()

            # Encrypt sensitive values if encryption is enabled
            if self.encryption_key:
                config_to_save = self._encrypt_config_values(config_to_save)

            if filename.endswith('.json'):
                with open(config_path, 'w') as f:
                    json.dump(config_to_save, f, indent=4)
            elif filename.endswith('.ini'):
                self._save_ini_config(config_to_save, config_path)
            else:
                logger.error(f"Unsupported config format: {filename}")
                return False

            logger.info(f"Configuration saved to {config_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving config {filename}: {e}")
            return False

    def _save_ini_config(self, config: Dict[str, Any], config_path: Path):
        """Save configuration as INI file"""
        parser = configparser.ConfigParser()

        for section, options in config.items():
            parser[section] = options

        with open(config_path, 'w') as f:
            parser.write(f)

    def create_default_config(self, config_path: Path) -> Dict[str, Any]:
        """Create default configuration file based on format"""
        if config_path.name.endswith('.json'):
            default_config = self._get_default_json_config()
        elif config_path.name.endswith('.ini'):
            default_config = self._get_default_ini_config()
        else:
            logger.error(f"Unsupported config format: {config_path.name}")
            return {}

        try:
            self.save_config(default_config, config_path.name)
            logger.info(f"Created default config at {config_path}")
            return default_config
        except Exception as e:
            logger.error(f"Error creating default config: {e}")
            return {}

    def _get_default_json_config(self) -> Dict[str, Any]:
        """Get default JSON configuration"""
        return {
            "database": {
                "path": "data/att.db",
                "auto_create": True,
                "encryption": False
            },
            "logging": {
                "level": "INFO",
                "file": "logs/app.log",
                "max_size_mb": 10,
                "backup_count": 5,
                "compress": True
            },
            "sync": {
                "interval_seconds": 300,
                "retry_attempts": 3,
                "retry_delay_seconds": 60,
                "batch_size": 100
            },
            "devices": [
                {
                    "ip": "192.168.1.201",
                    "port": 4370,
                    "serial_number": "DEVICE_SERIAL_NUMBER",
                    "name": "Main Entrance Device",
                    "enabled": True,
                    "timeout": 30
                }
            ],
            "server": {
                "url": "https://your-academy.example.com/",
                "api_key": "your_api_key_here",
                "sync_enabled": True,
                "verify_ssl": True,
                "timeout": 30
            },
            "security": {
                "encryption_enabled": False,
                "integrity_check": True,
                "auto_update": False
            },
            "application": {
                "auto_start": False,
                "minimize_to_tray": True,
                "check_for_updates": True,
                "auto_connect_devices": True,
                "language": "en"
            }
        }

    def _get_default_ini_config(self) -> Dict[str, Any]:
        """Get default INI configuration"""
        return {
            "Database": {
                "Path": "data/att.db",
                "AutoCreate": "true",
                "Encryption": "false"
            },
            "Logging": {
                "Level": "INFO",
                "File": "logs/app.log",
                "MaxSizeMB": "10",
                "BackupCount": "5",
                "Compress": "true"
            },
            "Sync": {
                "IntervalSeconds": "300",
                "RetryAttempts": "3",
                "RetryDelaySeconds": "60",
                "BatchSize": "100"
            },
            "Server": {
                "Url": "https://your-academy.example.com/",
                "ApiKey": "your_api_key_here",
                "SyncEnabled": "true",
                "VerifySSL": "true",
                "Timeout": "30"
            },
            "Security": {
                "EncryptionEnabled": "false",
                "IntegrityCheck": "true",
                "AutoUpdate": "false"
            },
            "Application": {
                "AutoStart": "false",
                "MinimizeToTray": "true",
                "CheckForUpdates": "true",
                "AutoConnectDevices": "true",
                "Language": "en"
            }
        }

    def _encrypt_config_values(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive configuration values"""
        # Simple encryption demonstration - in production use proper crypto libraries
        encrypted_config = config.copy()

        if isinstance(config, dict):
            for key, value in config.items():
                if isinstance(value, dict):
                    encrypted_config[key] = self._encrypt_config_values(value)
                elif self._is_sensitive_key(key):
                    encrypted_config[key] = self._simple_encrypt(str(value))

        return encrypted_config

    def _decrypt_config_values(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt sensitive configuration values"""
        decrypted_config = config.copy()

        if isinstance(config, dict):
            for key, value in config.items():
                if isinstance(value, dict):
                    decrypted_config[key] = self._decrypt_config_values(value)
                elif self._is_sensitive_key(key) and isinstance(value, str):
                    try:
                        decrypted_config[key] = self._simple_decrypt(value)
                    except:
                        # If decryption fails, keep original value
                        pass

        return decrypted_config

    # In your config manager, add encryption for API keys
    def _encrypt_sensitive_data(self, config):
        """Encrypt sensitive data in configuration"""
        encrypted_config = config.copy()

        # Encrypt API keys and sensitive data
        if 'server' in config and 'api_key' in config['server']:
            encrypted_config['server']['api_key'] = self._encrypt_string(
                config['server']['api_key']
            )

        return encrypted_config

    def _decrypt_sensitive_data(self, config):
        """Decrypt sensitive data in configuration"""
        decrypted_config = config.copy()

        # Decrypt API keys
        if 'server' in config and 'api_key' in config['server']:
            try:
                decrypted_config['server']['api_key'] = self._decrypt_string(
                    config['server']['api_key']
                )
            except:
                # If decryption fails, keep original
                pass

        return decrypted_config

    def _is_sensitive_key(self, key: str) -> bool:
        """Check if a configuration key contains sensitive data"""
        sensitive_keys = ['api_key', 'apikey', 'password', 'secret', 'token', 'key']
        return any(sensitive in key.lower() for sensitive in sensitive_keys)

    def _simple_encrypt(self, text: str) -> str:
        """Simple encryption for demonstration purposes"""
        # In production, use proper encryption like cryptography.fernet
        if not self.encryption_key:
            return text

        # Simple XOR encryption for demonstration
        encrypted = []
        for i, char in enumerate(text):
            key_char = self.encryption_key[i % len(self.encryption_key)]
            encrypted_char = chr(ord(char) ^ ord(key_char))
            encrypted.append(encrypted_char)

        return ''.join(encrypted)

    def _simple_decrypt(self, text: str) -> str:
        """Simple decryption for demonstration purposes"""
        if not self.encryption_key:
            return text

        # XOR decryption (same as encryption)
        return self._simple_encrypt(text)

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate configuration structure and values"""
        try:
            # Basic validation checks
            if not isinstance(config, dict):
                return False

            # Check required sections
            required_sections = ['database', 'logging', 'server', 'application']
            for section in required_sections:
                if section not in config:
                    logger.warning(f"Missing configuration section: {section}")
                    return False

            # Validate specific values
            if not self._validate_database_config(config.get('database', {})):
                return False

            if not self._validate_server_config(config.get('server', {})):
                return False

            return True

        except Exception as e:
            logger.error(f"Configuration validation error: {e}")
            return False

    def _validate_database_config(self, db_config: Dict[str, Any]) -> bool:
        """Validate database configuration"""
        if 'path' not in db_config:
            logger.error("Database path not specified")
            return False
        return True

    def _validate_server_config(self, server_config: Dict[str, Any]) -> bool:
        """Validate server configuration"""
        if 'url' not in server_config:
            logger.error("Server URL not specified")
            return False

        if 'api_key' not in server_config or server_config['api_key'] == 'your_api_key_here':
            logger.warning("API key not configured or using default value")

        return True

    def get_config_hash(self, config: Dict[str, Any]) -> str:
        """Calculate hash of configuration for integrity checking"""
        config_str = json.dumps(config, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()

# Utility function for easy configuration access
def get_config(config_file: str = "app_config.json") -> Dict[str, Any]:
    """Helper function to quickly load configuration"""
    manager = ConfigManager()
    return manager.load_config(config_file)

def save_config(config: Dict[str, Any], config_file: str = "app_config.json") -> bool:
    """Helper function to quickly save configuration"""
    manager = ConfigManager()
    return manager.save_config(config, config_file)
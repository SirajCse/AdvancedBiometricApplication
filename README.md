# Advanced Biometric Application

A comprehensive biometric attendance system for educational institutions using ZKTeco devices.

## Features

- Real-time attendance capture from ZKTeco biometric devices
- Automatic synchronization with central server
- Windows service installation for background operation
- Comprehensive logging and error handling
- Easy configuration management

## Installation

1. Run `install.bat` to set up the application
2. Configure your devices in `config/default_config.json`
3. Run `scripts/run_app.bat` to start the application

## Windows Service Installation

Run `scripts/install_service.bat` as administrator to install as a Windows service.

## Configuration

Edit `config/default_config.json` to configure:
- Device IP addresses and ports
- Server URL and API settings
- Sync intervals and retry policies
- Application behavior

## Support

For support and documentation, visit https://www.bitdreamit.com
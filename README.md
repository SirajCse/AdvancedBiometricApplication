# Advanced Biometric Application

A comprehensive biometric attendance system for public / private institutions using ZKTeco devices. This application provides real-time attendance capture, automatic synchronization with central servers, and Windows service operation.

## 📋 Table of Contents

- [🛠  Prerequisites](#-prerequisites)
- [✨ Features](#-features)  
- [🚀 Complete Installation Process](#-complete-installation-process)
- [🔧 Configuration](#-configuration)
- [🔒 Build Protected Executable](#-build-protected-executable)
- [⚙️ Configuration Setup](#%EF%B8%8F-configuration-setup)
- [📦 Installation Options](#-installation-options)
- [✅ Verification and Testing](#-verification-and-testing)
- [🏢 Production Deployment Checklist](#-production-deployment-checklist)
- [🐛 Troubleshooting](#-troubleshooting)
- [🔄 Maintenance and Updates](#-maintenance-and-updates)
- [📊 Support and Monitoring](#-support-and-monitoring)
- [🔐 License Management](#-license-management)

## 🛠 Prerequisites

- **Python 3.7+** installed on Windows
- **Administrator privileges** for service installation
- **Network access** to biometric devices
- **ZKTeco biometric devices** properly connected to network
- **Git** for version control

## ✨ Features

- **Real-time attendance capture** from ZKTeco biometric devices
- **Automatic synchronization** with central server
- **Windows service installation** for background operation
- **Comprehensive logging** and error handling
- **Easy configuration management** with JSON/INI support
- **Secure executable protection** with bytecode encryption
- **License key management** for commercial deployment
- **Multi-device support** with automatic reconnection
- **Integrity verification** against tampering

## 🚀 Complete Installation Process

### Step 1: Clone and Setup Repository

```bash
git clone https://github.com/SirajCse/AdvancedBiometricApplication.git
cd AdvancedBiometricApplication
```

### Step 2: Basic Installation

```cmd
# Run the main installer
install.bat
```

This will:
- Create required directories (`config`, `data`, `logs`, `scripts`)
- Install Python dependencies
- Set up basic configuration

### Step 3: Build Protected Executable

```cmd
# Set encryption key
set APP_ENCRYPTION_KEY=YourSecurePassword123!

# Build the protected executable
python build_protected.py
```

### Step 4: Service Installation (Administrator Required)

```cmd
# Run as Administrator
scripts\install_service.bat
```

### Step 5: License Activation

```cmd
# Generate a trial license
python generate_license.py

# Or activate with existing license
python activate_license.py
```

### Step 6: Verification

```cmd
# Test the service
sc query AdvancedBiometric

# Check logs
type logs\app.log
```

## 🔧 Configuration

### Configuration Files

- `config/default_config.json` - Primary configuration (JSON format)
- `config/app_config.ini` - Alternative configuration (INI format)

### Key Configuration Sections

```json
{
  "database": {
    "path": "data/att.db",
    "auto_create": true,
    "encryption": false
  },
  "logging": {
    "level": "INFO",
    "file": "logs/app.log",
    "max_size_mb": 10,
    "backup_count": 5
  },
  "devices": [
    {
      "ip": "192.168.1.201",
      "port": 4370,
      "serial_number": "DEVICE_SERIAL_NUMBER",
      "name": "Main Entrance Device",
      "enabled": true,
      "timeout": 30
    }
  ],
  "server": {
    "url": "https://your-academy.example.com/",
    "api_key": "your_api_key_here",
    "sync_enabled": true,
    "verify_ssl": true,
    "timeout": 30
  }
}
```

## 🔒 Build Protected Executable

### 1. Set Encryption Key

```cmd
set APP_ENCRYPTION_KEY=YourSecurePassword123!
```

### 2. Build the Application

```cmd
python build_protected.py
```

### 3. Verify Build Success

```cmd
dir dist
# Should show: AdvancedBiometricApplication.exe
```

### Security Features Applied

- Bytecode encryption with environment-based keys
- Runtime integrity checking
- Anti-debugging protection
- Secure file permissions
- Integrity hash verification

## ⚙️ Configuration Setup

### 1. Edit Device Configuration

Update `config/default_config.json` with your actual device information:

```json
{
  "devices": [
    {
      "ip": "192.168.1.201",
      "port": 4370,
      "serial_number": "ZKDevice12345",
      "name": "Main Entrance Device",
      "enabled": true
    }
  ],
  "server": {
    "url": "https://your-school-server.com/api/",
    "api_key": "your_actual_api_key_here",
    "sync_enabled": true
  }
}
```

### 2. Environment Variables (Optional)

```cmd
set BIOMETRIC_SERVER_URL=https://your-school-server.com/api/
set BIOMETRIC_API_KEY=your_actual_api_key_here
```

## 📦 Installation Options

### Option 1: Standard Application Installation

```cmd
install.bat
```

### Option 2: Windows Service Installation (Recommended)

```cmd
# Run as Administrator
scripts\install_service.bat
```

### Option 3: Manual Service Installation

```cmd
# Open Command Prompt as Administrator
cd AdvancedBiometricApplication
python src\main.py --install-service

# Verify service installation
sc query AdvancedBiometric
```

### Option 4: Foreground Mode (Testing)

```cmd
scripts\run_app.bat
```

## ✅ Verification and Testing

### 1. Test Application Functionality

```cmd
scripts\run_app.bat
```

### 2. Verify Device Connectivity

```cmd
python test_device.py
```

### 3. Test Service Operation

```cmd
# Start the service
sc start AdvancedBiometric

# Check service status
sc query AdvancedBiometric

# View logs
type logs\app.log
```

### 4. Test License System

```cmd
# Generate a license
python generate_license.py

# Check license info
python generate_license.py info
```

## 🏢 Production Deployment Checklist

### Security Hardening

```cmd
# Set secure permissions on all directories
icacls AdvancedBiometricApplication /inheritance:r /grant:r Administrators:(F)

# Secure configuration files
attrib +R config\default_config.json
```

### Integrity Verification

```cmd
# Verify executable integrity
python -c "
import hashlib
expected_hash = 'your_expected_hash_here'
with open('dist/AdvancedBiometricApplication.exe', 'rb') as f:
    current_hash = hashlib.sha256(f.read()).hexdigest()
print('Integrity check:', current_hash == expected_hash)
"
```

### Scheduled Tasks for Maintenance

```cmd
# Create scheduled task for log rotation
schtasks /create /tn \"BiometricAppLogCleanup\" /tr \"C:\AdvancedBiometricApplication\scripts\cleanup_logs.bat\" /sc daily /st 23:00
```

## 🐛 Troubleshooting Common Issues

### Device Connection Problems

```cmd
# Check device network connectivity
ping 192.168.1.201

# Test device port
telnet 192.168.1.201 4370

# Check firewall settings
netsh advfirewall firewall show rule name=all | findstr \"4370\"
```

### Service Installation Issues

```cmd
# Check if Python is in system PATH
python --version

# Verify administrator privileges
net session >nul 2>&1 && echo Administrator || echo Not administrator

# View detailed error information
python src\main.py --install-service --debug
```

### Database Issues

```cmd
# Check database file permissions
icacls data\att.db

# Verify database integrity
python -c "
import sqlite3
conn = sqlite3.connect('data/att.db')
print('Database integrity check:', conn.execute('PRAGMA integrity_check').fetchone())
conn.close()
"
```

## 🔄 Maintenance and Updates

### Regular Maintenance Tasks

```cmd
# Backup database
xcopy data\att.db backup\att.db_%DATE% /Y

# Rotate logs
python -c "
import logging
from logging.handlers import RotatingFileHandler
handler = RotatingFileHandler('logs/app.log', maxBytes=10*1024*1024, backupCount=5)
handler.doRollover()
"

# Check service health
sc query AdvancedBiometric | findstr \"STATE\"
```

### Update Procedure

```cmd
# Stop service
sc stop AdvancedBiometric

# Backup current installation
xcopy C:\AdvancedBiometricApplication C:\AdvancedBiometricApplication_backup_%DATE% /E /I

# Deploy new version
xcopy \\server\new_version\* C:\AdvancedBiometricApplication /E /Y

# Update integrity hash
set APP_EXPECTED_HASH=new_hash_value_here

# Start service
sc start AdvancedBiometric
```

## 📊 Support and Monitoring

### Monitoring Script

Create `health_check.bat`:

```batch
@echo off
python -c "
import requests
import socket
try:
    # Check service status
    # Check device connectivity
    # Check database health
    print('All systems operational')
except Exception as e:
    print('Error:', e)
"
```

### Log Monitoring

```cmd
# Tail application logs
powershell "Get-Content logs\app.log -Wait -Tail 50"
```

## 🔐 License Management

### Generate License Keys

```cmd
python generate_license.py
```

Follow the interactive prompts to generate license keys for customers.

### License File Structure

Licenses are stored in `config/license.json`:

```json
{
  "license_key": "A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6",
  "customer_name": "ABC Corporation",
  "device_count": 5,
  "issued_date": "2024-01-01T00:00:00.000000",
  "expiry_date": "2025-01-01T00:00:00.000000",
  "activated": true,
  "activation_date": "2024-01-01T00:00:00.000000"
}
```

### Environment Variables for License Security

```cmd
# Set secure salt for license generation
set LICENSE_SALT=YourSuperSecureSaltValue123!
```

## 📞 Support

For technical support and documentation:
- **Website**: https://www.bitdreamit.com
- **Email**: info@bitdreamit.com
- **GitHub Issues**: [Create Issue](https://github.com/SirajCse/AdvancedBiometricApplication/issues)

## 📄 License

This software requires a valid license key for production use. Generate trial licenses using the included license manager or contact support for commercial licenses.

---

**Note**: This application is designed for public / private institutions and requires proper ZKTeco biometric devices for full functionality. Always test in a development environment before production deployment.
```

## 📋 **Key Additions Made:**

1. **Complete Installation Process** - Step-by-step guide from clone to verification
2. **Multiple Installation Options** - Service vs foreground mode
3. **Service Scripts Documentation** - Proper usage of your comprehensive service scripts
4. **Administrator Requirements** - Clear indication of when admin rights are needed
5. **Verification Steps** - How to confirm everything is working
6. **Troubleshooting Section** - Common issues and solutions

This provides users with a complete, professional guide to installing and using your application! 🚀
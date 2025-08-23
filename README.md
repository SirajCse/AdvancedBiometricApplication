# Advanced Biometric Application

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue)](https://www.python.org/)
[![Windows](https://img.shields.io/badge/OS-Windows-lightgrey)]()
[![License](https://img.shields.io/badge/License-Proprietary-red)]()
[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen)]()
[![Device Connectivity](https://img.shields.io/badge/Device-Connected-green)]()
[![Service Health](https://img.shields.io/badge/Service-Running-green)]()

A professional-grade biometric attendance system connecting **ZKTeco devices** to your server with enhanced security and service integration.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Features](#features)
- [Configuration](#configuration)
- [Initial Setup](#initial-setup)
- [Build Protected Executable](#build-protected-executable)
- [Configuration Setup](#configuration-setup)
- [Installation Options](#installation-options)
- [Verification and Testing](#verification-and-testing)
- [Production Deployment Checklist](#production-deployment-checklist)
- [Troubleshooting](#troubleshooting)
- [Maintenance and Updates](#maintenance-and-updates)
- [Support and Monitoring](#support-and-monitoring)

---

## Prerequisites

1. **Python 3.7+** installed on Windows
2. **Administrator privileges** for service installation
3. **Network access** to biometric devices
4. **ZKTeco devices** properly connected to network

---

## Features

- Real-time attendance capture from ZKTeco biometric devices
- Automatic synchronization with central server
- Windows service installation for background operation
- Comprehensive logging and error handling
- Easy configuration management

---

## Configuration

Edit `config/default_config.json` to configure:
- Device IP addresses and ports
- Server URL and API settings
- Sync intervals and retry policies
- Application behavior

## Initial Setup

<details>
<summary>Download and Extract Application</summary>

```bash
mkdir C:\AdvancedBiometric
cd C:\AdvancedBiometric
````

</details>

<details>
<summary>Set Encryption Key</summary>

```cmd
set APP_ENCRYPTION_KEY=YourSecurePassword123!
```

*Must be at least 16 characters.*

</details>

---

## Build Protected Executable

<details>
<summary>Run Secure Build</summary>

```cmd
python build_protected.py
```

</details>

<details>
<summary>Alternative: Use Batch Installer</summary>

```cmd
install_protected.bat
```

</details>

<details>
<summary>Expected Build Output</summary>

```
BUILD COMPLETED SUCCESSFULLY!
Executable: dist/AdvancedBiometricApplication.exe
Integrity Hash: a1b2c3d4e5f6...
```

</details>

<details>
<summary>Secure the Integrity Information</summary>

```cmd
echo a1b2c3d4e5f6... > C:\secure\app_hash.txt
icacls C:\secure\app_hash.txt /inheritance:r /grant:r Administrators:(F)
```

</details>

---

## Configuration Setup

<details>
<summary>Edit Device Configuration</summary>

`config/default_config.json`:

```json
{
  "devices": [
    {"ip": "192.168.1.201", "port": 4370, "serial_number": "ZKDevice12345", "name": "Main Entrance Device", "enabled": true}
  ],
  "server": {"url": "https://your-school-server.com/api/", "api_key": "your_actual_api_key_here", "sync_enabled": true},
  "sync": {"interval_seconds": 300, "retry_attempts": 3}
}
```

</details>

<details>
<summary>Optional Environment Variables</summary>

```cmd
set BIOMETRIC_SERVER_URL=https://your-school-server.com/api/
set BIOMETRIC_API_KEY=your_actual_api_key_here
```

</details>

---

## Installation Options

<details>
<summary>Standard Installation</summary>

```cmd
install.bat
```

</details>

<details>
<summary>Windows Service Installation (Recommended)</summary>

```cmd
scripts\install_service.bat
```

</details>

<details>
<summary>Manual Service Installation</summary>

```cmd
cd C:\AdvancedBiometric
python src\main.py --install-service
sc query AdvancedBiometric
```

</details>

---

## Verification and Testing

<details>
<summary>Run Application in Foreground</summary>

```cmd
scripts\run_app.bat
```

</details>

<details>
<summary>Verify Device Connectivity</summary>

```cmd
python -c "
from src.biometric.zk_device import ZKDevice
device = ZKDevice('192.168.1.201', 4370)
if device.connect(): print('Device connected successfully')
else: print('Connection failed')
"
```

</details>

<details>
<summary>Test Service Operation</summary>

```cmd
sc start AdvancedBiometric
sc query AdvancedBiometric
type logs\app.log
```

</details>

---

## Production Deployment Checklist

<details>
<summary>Security Hardening</summary>

```cmd
icacls C:\AdvancedBiometric /inheritance:r /grant:r Administrators:(F) /grant:r SYSTEM:(F) /grant:r Users:(RX)
attrib +R config\default_config.json
```

</details>

<details>
<summary>Verify Integrity</summary>

```cmd
python -c "
from src.utils.windows_utils import WindowsStartupManager
import os

expected_hash = os.environ.get('APP_EXPECTED_HASH')
if WindowsStartupManager.verify_executable_integrity('dist/AdvancedBiometricApplication.exe', expected_hash):
    print('Integrity verification PASSED')
else:
    print('Integrity verification FAILED')
"
```

</details>

<details>
<summary>Scheduled Maintenance</summary>

```cmd
schtasks /create /tn "BiometricAppLogCleanup" /tr "C:\AdvancedBiometric\scripts\cleanup_logs.bat" /sc daily /st 23:00
```

</details>

---

## Troubleshooting

<details>
<summary>Device Connection Issues</summary>

```cmd
ping 192.168.1.201
telnet 192.168.1.201 4370
netsh advfirewall firewall show rule name=all | findstr "4370"
```

</details>

<details>
<summary>Service Installation Issues</summary>

```cmd
python --version
net session >nul 2>&1 && echo Administrator || echo Not administrator
python src\main.py --install-service --debug
```

</details>

<details>
<summary>Database Issues</summary>

```cmd
icacls data\att.db
python -c "
import sqlite3
conn = sqlite3.connect('data/att.db')
print('Database integrity check:', conn.execute('PRAGMA integrity_check').fetchone())
conn.close()
"
```

</details>

---

## Maintenance and Updates

<details>
<summary>Regular Maintenance Tasks</summary>

```cmd
# Backup database
xcopy data\att.db backup\att.db_%DATE% /Y

# Rotate logs
python -c "
from logging.handlers import RotatingFileHandler
handler = RotatingFileHandler('logs/app.log', maxBytes=10*1024*1024, backupCount=5)
handler.doRollover()
"

# Check service health
sc query AdvancedBiometric | findstr "STATE"
```

</details>

<details>
<summary>Update Procedure</summary>

```cmd
sc stop AdvancedBiometric
xcopy C:\AdvancedBiometric C:\AdvancedBiometric_backup_%DATE% /E /I
xcopy \\server\new_version\* C:\AdvancedBiometric /E /Y
set APP_EXPECTED_HASH=new_hash_value_here
sc start AdvancedBiometric
```

</details>

---

## Support and Monitoring

<details>
<summary>Monitoring Script</summary>

```cmd
@echo off
python -c "
import requests
import socket
try: print('All systems operational')
except Exception as e: print('Error:', e)
"
```

</details>

<details>
<summary>Log Monitoring</summary>

```cmd
powershell "Get-Content logs\app.log -Wait -Tail 50"
```

</details>

---


## Support

For support and documentation, visit https://www.bitdreamit.com
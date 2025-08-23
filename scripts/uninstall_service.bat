@echo off
chcp 65001 >nul
title Advanced Biometric Application - Uninstall Service

echo ===============================================
echo    Advanced Biometric Application Service Uninstaller
echo ===============================================
echo.

:: Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Error: This script must be run as Administrator!
    echo Right-click on the file and select "Run as administrator"
    pause
    exit /b 1
)

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.7 or higher from https://python.org
    pause
    exit /b 1
)

echo Uninstalling Advanced Biometric Application Windows service...
echo.

:: Change to script directory
cd /d "%~dp0"

:: Stop the service first
echo Stopping the service...
sc stop AdvancedBiometric >nul 2>&1
timeout /t 3 /nobreak >nul

:: Uninstall the service
python ..\src\main.py --uninstall-service

if %errorlevel% equ 0 (
    echo.
    echo Service uninstalled successfully!
    echo.
    echo The service has been removed from the system.
) else (
    echo.
    echo Error: Failed to uninstall the service.
    echo The service may not have been installed, or there may be permission issues.
    echo.
    echo Trying alternative uninstall method...
    sc delete AdvancedBiometric
    if %errorlevel% equ 0 (
        echo Service removed using alternative method.
    ) else (
        echo Could not remove service. It may not exist or you may need to reboot.
    )
)

echo.
echo Uninstallation process completed.
pause
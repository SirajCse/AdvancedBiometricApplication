@echo off
chcp 65001 >nul
title Advanced Biometric Application - Install Service

echo ===============================================
echo    Advanced Biometric Application Service Installer
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

echo Installing Advanced Biometric Application as a Windows service...
echo.

:: Change to script directory
cd /d "%~dp0"

:: Install the service
python ..\src\main.py --install-service

if %errorlevel% equ 0 (
    echo.
    echo Service installed successfully!
    echo.
    echo The service has been installed with the following settings:
    echo Service Name: AdvancedBiometric
    echo Display Name: Advanced Biometric Application
    echo Startup Type: Automatic
    echo.
    echo You can manage the service using:
    echo - Services.msc (Windows Services Manager)
    echo - sc start AdvancedBiometric
    echo - sc stop AdvancedBiometric
    echo - sc query AdvancedBiometric
    echo.
    echo Starting the service...
    sc start AdvancedBiometric
    if %errorlevel% equ 0 (
        echo Service started successfully!
    ) else (
        echo Warning: Service installed but could not be started automatically.
        echo You may need to start it manually from Services.msc
    )
) else (
    echo.
    echo Error: Failed to install the service.
    echo Please check the logs for more information.
)

echo.
echo Installation process completed.
pause
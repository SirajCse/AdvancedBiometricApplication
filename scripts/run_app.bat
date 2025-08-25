@echo off
chcp 65001 >nul
title Advanced Biometric Application

echo ===============================================
echo    Advanced Biometric Application
echo ===============================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.7 or higher from https://python.org
    pause
    exit /b 1
)

echo Starting Advanced Biometric Application...
echo.
echo Application will run in the foreground.
echo Press Ctrl+C to stop the application.
echo.

:: Change to script directory
cd /d "%~dp0"

:: Check if required directories exist
if not exist ..\data (
    echo Creating data directory...
    mkdir ..\data
)

if not exist ..\logs (
    echo Creating logs directory...
    mkdir ..\logs
)

if not exist ..\config (
    echo Creating config directory...
    mkdir ..\config
)

:: Check if config files exist
if not exist ..\config\default_config.json (
    echo Warning: default_config.json not found in config directory.
    echo The application will create a default configuration.
)

:: Check if license is activated
if not exist ..\config\license.json (
    echo Warning: No license found. Running in trial mode.
    timeout /t 2 /nobreak >nul

:: Run the application
python ..\src\main.py

if %errorlevel% equ 0 (
    echo.
    echo Application exited normally.
) else (
    echo.
    echo Application exited with an error (code: %errorlevel%).
    echo Please check the logs in the logs directory for details.
)

echo.
pause


:: install_protected.bat
@echo off
chcp 65001 >nul
title Advanced Biometric Application - Protected Build

echo ===============================================
echo    Advanced Biometric Application - Protected Build
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

:: Create directory structure
echo Creating directory structure...
if not exist config mkdir config
if not exist data mkdir data
if not exist logs mkdir logs
if not exist scripts mkdir scripts
if not exist dist mkdir dist

:: Install protection tools
echo Installing protection tools...
pip install pyinstaller pyarmor

if errorlevel 1 (
    echo Error installing protection tools.
    pause
    exit /b 1
)

:: Build protected executable
echo Building protected executable...
python build_protected.py

if errorlevel 1 (
    echo Error building protected executable.
    pause
    exit /b 1
)

:: Apply additional protections
echo Applying additional protections...
python -c "
import sys
sys.path.append('src')
from utils.windows_utils import WindowsStartupManager
WindowsStartupManager.protect_executable('dist/AdvancedBiometricApplication.exe')
"

echo.
echo ===============================================
echo    PROTECTED BUILD COMPLETED SUCCESSFULLY!
echo ===============================================
echo.
echo The protected executable has been created in:
echo   dist\AdvancedBiometricApplication.exe
echo.
echo Security features applied:
echo - Bytecode encryption
echo - Code obfuscation
echo - Anti-debugging measures
echo - Anti-tampering protection
echo - File permission restrictions
echo.
echo Note: For maximum protection, consider:
echo 1. Purchasing a code signing certificate
echo 2. Using professional obfuscation tools
echo 3. Implementing custom packers
echo.
pause
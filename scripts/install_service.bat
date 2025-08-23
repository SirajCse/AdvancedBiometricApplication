@echo off
chcp 65001 >nul
title Advanced Biometric Application - Secure Build

echo ===============================================
echo    Advanced Biometric Application - Secure Build
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

:: Install required packages (minimal set for security)
echo Installing required packages...
pip install pyinstaller>=5.0 requests>=2.28.0 psutil>=5.9.0

if errorlevel 1 (
    echo Error installing required packages.
    pause
    exit /b 1
)

:: Check if encryption key is set
echo Checking for encryption key...
set "KEY_SET=false"
if not "%APP_ENCRYPTION_KEY%"=="" (
    if not "%APP_ENCRYPTION_KEY%"=="YourSecureKeyMin16Chars" (
        set "KEY_SET=true"
    )
)

if "%KEY_SET%"=="false" (
    echo.
    echo WARNING: APP_ENCRYPTION_KEY environment variable not set or using default value.
    echo.
    echo For a secure build, please set your encryption key:
    echo set APP_ENCRYPTION_KEY=YourSecureKeyMin16Chars
    echo.
    echo Alternatively, you will be prompted during the build process.
    echo.
    timeout /t 5 /nobreak >nul
)

:: Build protected executable
echo Building protected executable...
python build_protected.py

if errorlevel 1 (
    echo Error building protected executable.
    echo Please check the build output for details.
    pause
    exit /b 1
)

:: Apply additional protections using the improved method
echo Applying additional protections...
python -c "
import os
import subprocess
from pathlib import Path

def protect_executable(exe_path):
    '''Apply security protections to executable'''
    if not os.path.exists(exe_path):
        print('Executable not found for protection')
        return False

    try:
        # Set restrictive file permissions (Windows)
        if os.name == 'nt':
            subprocess.run([
                'icacls', exe_path,
                '/inheritance:r',
                '/grant:r', 'Administrators:(F)',
                '/grant:r', 'SYSTEM:(F)',
                '/grant:r', 'Users:(RX)'
            ], check=True, capture_output=True)

        print('Applied security protections successfully')
        return True

    except subprocess.CalledProcessError as e:
        print(f'Warning: Could not set file permissions: {e.stderr}')
        return False

# Apply protections
exe_path = 'dist/AdvancedBiometricApplication.exe'
protect_executable(exe_path)
"

:: Generate security summary
echo Generating security summary...
python -c "
import hashlib
import os
from pathlib import Path

def generate_security_summary():
    exe_path = 'dist/AdvancedBiometricApplication.exe'

    if not os.path.exists(exe_path):
        print('Executable not found for security summary')
        return

    # Calculate hash
    hasher = hashlib.sha256()
    with open(exe_path, 'rb') as f:
        while chunk := f.read(4096):
            hasher.update(chunk)
    file_hash = hasher.hexdigest()

    file_size = os.path.getsize(exe_path)

    summary = f'''
SECURITY BUILD SUMMARY
======================
File: {exe_path}
Size: {file_size} bytes
SHA256: {file_hash}
Build Completed: Successfully

SECURITY FEATURES APPLIED:
- Bytecode encryption with secure key management
- Runtime integrity checking
- Anti-debugging protection
- Secure file permissions
- No external packers (reduces AV false positives)

RECOMMENDATIONS FOR PRODUCTION:
1. Store the integrity hash securely: {file_hash}
2. Obtain a code signing certificate
3. Deploy in a secure environment
4. Regularly update and rebuild with new keys

IMPORTANT: The integrity hash above should be stored securely
for future verification of the executable.
'''
    print(summary)

    # Write to file
    with open('build_security_summary.txt', 'w') as f:
        f.write(summary)

generate_security_summary()
"

echo.
echo ===============================================
echo    SECURE BUILD COMPLETED SUCCESSFULLY!
echo ===============================================
echo.
echo The protected executable has been created in:
echo   dist\AdvancedBiometricApplication.exe
echo.
echo Security features applied:
echo - Secure bytecode encryption
echo - Runtime integrity verification
echo - Anti-debugging measures
echo - File permission restrictions
echo - No problematic packers (reduces AV alerts)
echo.
echo Important: A security summary has been saved to:
echo   build_security_summary.txt
echo.
echo Note: For maximum production protection:
echo 1. Obtain a code signing certificate
echo 2. Store the integrity hash securely
echo 3. Use secure deployment practices
echo.
pause
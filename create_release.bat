@echo off
echo Creating Release Package...
echo.

set VERSION=1.0.0
set RELEASE_DIR=Releases\AdvancedBiometricApplication_v%VERSION%

echo Creating directory structure...
if not exist %RELEASE_DIR% mkdir %RELEASE_DIR%
if not exist %RELEASE_DIR%\config mkdir %RELEASE_DIR%\config
if not exist %RELEASE_DIR%\data mkdir %RELEASE_DIR%\data
if not exist %RELEASE_DIR%\logs mkdir %RELEASE_DIR%\logs
if not exist %RELEASE_DIR%\scripts mkdir %RELEASE_DIR%\scripts

echo Copying files...
copy dist\AdvancedBiometricApplication.exe %RELEASE_DIR%\
copy config\default_config.json %RELEASE_DIR%\config\
copy config\app_config.ini %RELEASE_DIR%\config\
copy scripts\*.bat %RELEASE_DIR%\scripts\
copy LICENSE.txt %RELEASE_DIR%\
copy README.md %RELEASE_DIR%\
copy requirements.txt %RELEASE_DIR%\

echo Creating ZIP package...
cd Releases
powershell -command "Compress-Archive -Path AdvancedBiometricApplication_v%VERSION% -DestinationPath AdvancedBiometricApplication_v%VERSION%.zip"
cd ..

echo.
echo Release package created: Releases\AdvancedBiometricApplication_v%VERSION%.zip
echo.
pause
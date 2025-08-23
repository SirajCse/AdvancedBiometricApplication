:: Create service scripts
echo Creating service scripts...
echo @echo off >scripts\install_service.bat
echo chcp 65001 ^>nul >>scripts\install_service.bat
echo title Advanced Biometric Application - Install Service >>scripts\install_service.bat
echo. >>scripts\install_service.bat
echo echo =============================================== >>scripts\install_service.bat
echo echo    Advanced Biometric Application Service Installer >>scripts\install_service.bat
echo echo =============================================== >>scripts\install_service.bat
echo echo. >>scripts\install_service.bat
echo. >>scripts\install_service.bat
echo :: Check if running as administrator >>scripts\install_service.bat
echo net session ^>nul 2^>^&1 >>scripts\install_service.bat
echo if %%errorLevel%% neq 0 ( >>scripts\install_service.bat
echo     echo Error: This script must be run as Administrator! >>scripts\install_service.bat
echo     echo Right-click on the file and select "Run as administrator" >>scripts\install_service.bat
echo     pause >>scripts\install_service.bat
echo     exit /b 1 >>scripts\install_service.bat
echo ) >>scripts\install_service.bat
echo. >>scripts\install_service.bat
echo :: Check if Python is installed >>scripts\install_service.bat
echo python --version ^>nul 2^>^&1 >>scripts\install_service.bat
echo if errorlevel 1 ( >>scripts\install_service.bat
echo     echo Error: Python is not installed or not in PATH. >>scripts\install_service.bat
echo     echo Please install Python 3.7 or higher from https://python.org >>scripts\install_service.bat
echo     pause >>scripts\install_service.bat
echo     exit /b 1 >>scripts\install_service.bat
echo ) >>scripts\install_service.bat
echo. >>scripts\install_service.bat
echo echo Installing Advanced Biometric Application as a Windows service... >>scripts\install_service.bat
echo echo. >>scripts\install_service.bat
echo. >>scripts\install_service.bat
echo :: Change to script directory >>scripts\install_service.bat
echo cd /d "%%~dp0" >>scripts\install_service.bat
echo. >>scripts\install_service.bat
echo :: Install the service >>scripts\install_service.bat
echo python ..\src\main.py --install-service >>scripts\install_service.bat
echo. >>scripts\install_service.bat
echo if %%errorlevel%% equ 0 ( >>scripts\install_service.bat
echo     echo. >>scripts\install_service.bat
echo     echo Service installed successfully! >>scripts\install_service.bat
echo     echo. >>scripts\install_service.bat
echo     echo The service has been installed with the following settings: >>scripts\install_service.bat
echo     echo Service Name: AdvancedBiometric >>scripts\install_service.bat
echo     echo Display Name: Advanced Biometric Application >>scripts\install_service.bat
echo     echo Startup Type: Automatic >>scripts\install_service.bat
echo     echo. >>scripts\install_service.bat
echo     echo You can manage the service using: >>scripts\install_service.bat
echo     echo - Services.msc (Windows Services Manager) >>scripts\install_service.bat
echo     echo - sc start AdvancedBiometric >>scripts\install_service.bat
echo     echo - sc stop AdvancedBiometric >>scripts\install_service.bat
echo     echo - sc query AdvancedBiometric >>scripts\install_service.bat
echo     echo. >>scripts\install_service.bat
echo     echo Starting the service... >>scripts\install_service.bat
echo     sc start AdvancedBiometric >>scripts\install_service.bat
echo     if %%errorlevel%% equ 0 ( >>scripts\install_service.bat
echo         echo Service started successfully! >>scripts\install_service.bat
echo     ) else ( >>scripts\install_service.bat
echo         echo Warning: Service installed but could not be started automatically. >>scripts\install_service.bat
echo         echo You may need to start it manually from Services.msc >>scripts\install_service.bat
echo     ) >>scripts\install_service.bat
echo ) else ( >>scripts\install_service.bat
echo     echo. >>scripts\install_service.bat
echo     echo Error: Failed to install the service. >>scripts\install_service.bat
echo     echo Please check the logs for more information. >>scripts\install_service.bat
echo ) >>scripts\install_service.bat
echo. >>scripts\install_service.bat
echo echo. >>scripts\install_service.bat
echo echo Installation process completed. >>scripts\install_service.bat
echo pause >>scripts\install_service.bat

echo @echo off >scripts\uninstall_service.bat
echo chcp 65001 ^>nul >>scripts\uninstall_service.bat
echo title Advanced Biometric Application - Uninstall Service >>scripts\uninstall_service.bat
echo. >>scripts\uninstall_service.bat
echo echo =============================================== >>scripts\uninstall_service.bat
echo echo    Advanced Biometric Application Service Uninstaller >>scripts\uninstall_service.bat
echo echo =============================================== >>scripts\uninstall_service.bat
echo echo. >>scripts\uninstall_service.bat
echo. >>scripts\uninstall_service.bat
echo :: Check if running as administrator >>scripts\uninstall_service.bat
echo net session ^>nul 2^>^&1 >>scripts\uninstall_service.bat
echo if %%errorLevel%% neq 0 ( >>scripts\uninstall_service.bat
echo     echo Error: This script must be run as Administrator! >>scripts\uninstall_service.bat
echo     echo Right-click on the file and select "Run as administrator" >>scripts\uninstall_service.bat
echo     pause >>scripts\uninstall_service.bat
echo     exit /b 1 >>scripts\uninstall_service.bat
echo ) >>scripts\uninstall_service.bat
echo. >>scripts\uninstall_service.bat
echo :: Check if Python is installed >>scripts\uninstall_service.bat
echo python --version ^>nul 2^>^&1 >>scripts\uninstall_service.bat
echo if errorlevel 1 ( >>scripts\uninstall_service.bat
echo     echo Error: Python is not installed or not in PATH. >>scripts\uninstall_service.bat
echo     echo Please install Python 3.7 or higher from https://python.org >>scripts\uninstall_service.bat
echo     pause >>scripts\uninstall_service.bat
echo     exit /b 1 >>scripts\uninstall_service.bat
echo ) >>scripts\uninstall_service.bat
echo. >>scripts\uninstall_service.bat
echo echo Uninstalling Advanced Biometric Application Windows service... >>scripts\uninstall_service.bat
echo echo. >>scripts\uninstall_service.bat
echo. >>scripts\uninstall_service.bat
echo :: Change to script directory >>scripts\uninstall_service.bat
echo cd /d "%%~dp0" >>scripts\uninstall_service.bat
echo. >>scripts\uninstall_service.bat
echo :: Stop the service first >>scripts\uninstall_service.bat
echo echo Stopping the service... >>scripts\uninstall_service.bat
echo sc stop AdvancedBiometric ^>nul 2^>^&1 >>scripts\uninstall_service.bat
echo timeout /t 3 /nobreak ^>nul >>scripts\uninstall_service.bat
echo. >>scripts\uninstall_service.bat
echo :: Uninstall the service >>scripts\uninstall_service.bat
echo python ..\src\main.py --uninstall-service >>scripts\uninstall_service.bat
echo. >>scripts\uninstall_service.bat
echo if %%errorlevel%% equ 0 ( >>scripts\uninstall_service.bat
echo     echo. >>scripts\uninstall_service.bat
echo     echo Service uninstalled successfully! >>scripts\uninstall_service.bat
echo     echo. >>scripts\uninstall_service.bat
echo     echo The service has been removed from the system. >>scripts\uninstall_service.bat
echo ) else ( >>scripts\uninstall_service.bat
echo     echo. >>scripts\uninstall_service.bat
echo     echo Error: Failed to uninstall the service. >>scripts\uninstall_service.bat
echo     echo The service may not have been installed, or there may be permission issues. >>scripts\uninstall_service.bat
echo     echo. >>scripts\uninstall_service.bat
echo     echo Trying alternative uninstall method... >>scripts\uninstall_service.bat
echo     sc delete AdvancedBiometric >>scripts\uninstall_service.bat
echo     if %%errorlevel%% equ 0 ( >>scripts\uninstall_service.bat
echo         echo Service removed using alternative method. >>scripts\uninstall_service.bat
echo     ) else ( >>scripts\uninstall_service.bat
echo         echo Could not remove service. It may not exist or you may need to reboot. >>scripts\uninstall_service.bat
echo     ) >>scripts\uninstall_service.bat
echo ) >>scripts\uninstall_service.bat
echo. >>scripts\uninstall_service.bat
echo echo. >>scripts\uninstall_service.bat
echo echo Uninstallation process completed. >>scripts\uninstall_service.bat
echo pause >>scripts\uninstall_service.bat

echo @echo off >scripts\run_app.bat
echo chcp 65001 ^>nul >>scripts\run_app.bat
echo title Advanced Biometric Application >>scripts\run_app.bat
echo. >>scripts\run_app.bat
echo echo =============================================== >>scripts\run_app.bat
echo echo    Advanced Biometric Application >>scripts\run_app.bat
echo echo =============================================== >>scripts\run_app.bat
echo echo. >>scripts\run_app.bat
echo. >>scripts\run_app.bat
echo :: Check if Python is installed >>scripts\run_app.bat
echo python --version ^>nul 2^>^&1 >>scripts\run_app.bat
echo if errorlevel 1 ( >>scripts\run_app.bat
echo     echo Error: Python is not installed or not in PATH. >>scripts\run_app.bat
echo     echo Please install Python 3.7 or higher from https://python.org >>scripts\run_app.bat
echo     pause >>scripts\run_app.bat
echo     exit /b 1 >>scripts\run_app.bat
echo ) >>scripts\run_app.bat
echo. >>scripts\run_app.bat
echo echo Starting Advanced Biometric Application... >>scripts\run_app.bat
echo echo. >>scripts\run_app.bat
echo echo Application will run in the foreground. >>scripts\run_app.bat
echo echo Press Ctrl+C to stop the application. >>scripts\run_app.bat
echo echo. >>scripts\run_app.bat
echo. >>scripts\run_app.bat
echo :: Change to script directory >>scripts\run_app.bat
echo cd /d "%%~dp0" >>scripts\run_app.bat
echo. >>scripts\run_app.bat
echo :: Check if required directories exist >>scripts\run_app.bat
echo if not exist ..\data ( >>scripts\run_app.bat
echo     echo Creating data directory... >>scripts\run_app.bat
echo     mkdir ..\data >>scripts\run_app.bat
echo ) >>scripts\run_app.bat
echo. >>scripts\run_app.bat
echo if not exist ..\logs ( >>scripts\run_app.bat
echo     echo Creating logs directory... >>scripts\run_app.bat
echo     mkdir ..\logs >>scripts\run_app.bat
echo ) >>scripts\run_app.bat
echo. >>scripts\run_app.bat
echo if not exist ..\config ( >>scripts\run_app.bat
echo     echo Creating config directory... >>scripts\run_app.bat
echo     mkdir ..\config >>scripts\run_app.bat
echo ) >>scripts\run_app.bat
echo. >>scripts\run_app.bat
echo :: Check if config files exist >>scripts\run_app.bat
echo if not exist ..\config\default_config.json ( >>scripts\run_app.bat
echo     echo Warning: default_config.json not found in config directory. >>scripts\run_app.bat
echo     echo The application will create a default configuration. >>scripts\run_app.bat
echo ) >>scripts\run_app.bat
echo. >>scripts\run_app.bat
echo :: Run the application >>scripts\run_app.bat
echo python ..\src\main.py >>scripts\run_app.bat
echo. >>scripts\run_app.bat
echo if %%errorlevel%% equ 0 ( >>scripts\run_app.bat
echo     echo. >>scripts\run_app.bat
echo     echo Application exited normally. >>scripts\run_app.bat
echo ) else ( >>scripts\run_app.bat
echo     echo. >>scripts\run_app.bat
echo     echo Application exited with an error (code: %%errorlevel%%). >>scripts\run_app.bat
echo     echo Please check the logs in the logs directory for details. >>scripts\run_app.bat
echo ) >>scripts\run_app.bat
echo. >>scripts\run_app.bat
echo echo. >>scripts\run_app.bat
echo pause >>scripts\run_app.bat
# setup.py
from cx_Freeze import setup, Executable
import sys
import os

# Application information
APP_NAME = "Advanced Biometric Application"
APP_VERSION = "2.0"
APP_DESCRIPTION = "Biometric attendance system"
APP_AUTHOR = "Advanced Biometric Application"
APP_AUTHOR_EMAIL = "info@bitdreamit.com"

# Dependencies
build_exe_options = {
    "packages": [
        "os", "sys", "sqlite3", "datetime", "json", "logging", 
        "threading", "queue", "time", "socket", "winreg", "subprocess",
        "pathlib", "argparse", "struct", "requests", "urllib3"
    ],
    "include_files": [
        ("config/", "config/"),
        ("data/", "data/"),
        ("logs/", "logs/"),
        ("scripts/", "scripts/"),
    ],
    "excludes": ["tkinter", "test", "unittest", "email"],
    "optimize": 2,
    "include_msvcr": True,
}

# Executable configuration
executables = [
    Executable(
        "src/main.py",
        base="Win32GUI" if sys.platform == "win32" else None,
        target_name="AdvancedBiometric.exe",
        icon=None,  # Add icon path if available
    )
]

setup(
    name=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    author=APP_AUTHOR,
    author_email=APP_AUTHOR_EMAIL,
    options={"build_exe": build_exe_options},
    executables=executables,
)
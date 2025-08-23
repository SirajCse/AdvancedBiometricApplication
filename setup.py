# setup.py
from cx_Freeze import setup, Executable
import sys
import os
import PyInstaller
import subprocess
from pathlib import Path

# Application information
APP_NAME = "Advanced Biometric Application"
APP_VERSION = "2.0"
APP_DESCRIPTION = "Biometric attendance system"
APP_AUTHOR = "Advanced Biometric"
APP_AUTHOR_EMAIL = "info@bitdreamit.com"

# Build options for cx_Freeze
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
    # Obfuscation and protection settings
    "replace_paths": [("*", "")],  # Remove path information
    "silent": True,  # Reduce build output
}

# Executable configuration
executables = [
    Executable(
        "src/main.py",
        base="Win32GUI" if sys.platform == "win32" else None,
        target_name="AdvancedBiometricApplication.exe",
        icon=None,
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

# Additional protection steps
def apply_code_protection():
    """Apply additional code protection measures"""
    print("Applying code protection measures...")
    
    # 1. Create a dedicated build script for PyInstaller (better protection)
    create_pyinstaller_script()
    
    # 2. Obfuscate the source code before building
    obfuscate_code()
    
    # 3. Create a custom runtime for additional protection
    create_custom_runtime()
    
    print("Code protection measures applied successfully!")

def create_pyinstaller_script():
    """Create a PyInstaller build script for better protection"""
    pyinstaller_script = """
# PyInstaller build script with enhanced protection
import PyInstaller.__main__
import os

PyInstaller.__main__.run([
    'src/main.py',
    '--name=AdvancedBiometricApplication',
    '--onefile',
    '--windowed',
    '--icon=NONE',
    '--add-data=config;config',
    '--add-data=data;data',
    '--add-data=scripts;scripts',
    '--hidden-import=sqlite3',
    '--hidden-import=requests',
    '--hidden-import=urllib3',
    '--hidden-import=logging',
    '--clean',
    '--noconfirm',
    # Protection options
    '--key=YourEncryptionKey123!',  # Encryption key for bytecode
    '--upx-dir=upx',  # Use UPX compression
])
"""
    with open('build_pyinstaller.py', 'w') as f:
        f.write(pyinstaller_script)

def obfuscate_code():
    """Obfuscate Python code before building"""
    print("Obfuscating source code...")
    
    # This is a simple obfuscation example
    # For production, use professional obfuscation tools like PyArmor
    
    obfuscation_script = """
# Basic code obfuscation script
import os
import base64
import zlib
from pathlib import Path

def simple_obfuscate(file_path):
    \"\"\"Simple code obfuscation\"\"\"
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simple transformation (not secure, just example)
        obfuscated = base64.b64encode(zlib.compress(content.encode('utf-8')))
        
        # Create obfuscated version
        obfuscated_path = file_path + '.obfuscated'
        with open(obfuscated_path, 'wb') as f:
            f.write(b'# Obfuscated code\\n')
            f.write(b'import base64,zlib\\n')
            f.write(b'exec(zlib.decompress(base64.b64decode("\\n')
            f.write(obfuscated)
            f.write(b'")))\\n')
            
    except Exception as e:
        print(f"Error obfuscating {file_path}: {e}")

# Obfuscate main files
for py_file in Path('src').rglob('*.py'):
    if py_file.name != '__init__.py':
        simple_obfuscate(str(py_file))
"""
    
    with open('obfuscate_code.py', 'w') as f:
        f.write(obfuscation_script)
    
    # Run obfuscation
    try:
        subprocess.run([sys.executable, 'obfuscate_code.py'], check=True)
    except:
        print("Obfuscation skipped or failed")

def create_custom_runtime():
    """Create custom runtime hooks for additional protection"""
    runtime_hook = """
# Custom runtime hook for additional protection
import sys
import os
import hashlib

def verify_integrity():
    \"\"\"Verify application integrity\"\"\"
    expected_hash = "your_expected_hash_here"
    current_file = sys.argv[0]
    
    with open(current_file, 'rb') as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    
    if file_hash != expected_hash:
        print("Integrity check failed! Application may be tampered with.")
        sys.exit(1)

def anti_debug():
    \"\"\"Basic anti-debugging measures\"\"\"
    try:
        if hasattr(sys, 'gettrace') and sys.gettrace() is not None:
            print("Debugger detected! Exiting.")
            sys.exit(1)
    except:
        pass

# Run protection measures
anti_debug()
# verify_integrity()  # Enable after setting proper hash
"""
    
    with open('custom_runtime.py', 'w') as f:
        f.write(runtime_hook)

if __name__ == "__main__":
    apply_code_protection()
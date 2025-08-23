# build_protected.py
import os
import sys
import subprocess
import shutil
import tempfile
from pathlib import Path
import PyInstaller.__main__

def build_protected_exe():
    """Build a protected executable with multiple security layers"""

    print("=" * 60)
    print("Building Protected Advanced Biometric Application")
    print("=" * 60)

    # Step 1: Clean previous builds
    clean_previous_builds()

    # Step 2: Install required packages
    install_requirements()

    # Step 3: Use PyInstaller for better protection
    build_with_pyinstaller()

    # Step 4: Apply additional protections
    apply_post_build_protections()

    print("Build completed successfully!")
    print("Protected executable available in 'dist' directory")

def clean_previous_builds():
    """Clean previous build artifacts"""
    for dir_name in ['build', 'dist', '__pycache__']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Cleaned {dir_name} directory")

    # Clean obfuscated files
    for obf_file in Path('src').rglob('*.obfuscated'):
        obf_file.unlink()

def install_requirements():
    """Install required packages including protection tools"""
    requirements = [
        "pyinstaller>=5.0",
        "pyarmor>=7.0",  # Professional obfuscation tool
        "requests>=2.28.0",
        "cx_Freeze>=6.15.0",
        "psutil>=5.9.0"
    ]

    print("Installing requirements...")
    for package in requirements:
        subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)

def build_with_pyinstaller():
    """Build using PyInstaller with protection options"""
    print("Building with PyInstaller (better protection)...")

    pyinstaller_args = [
        "src/main.py",
        "--name=AdvancedBiometricApplication",
        "--onefile",
        "--windowed",
        "--clean",
        "--noconfirm",
        "--add-data=config;config",
        "--add-data=data;data",
        "--add-data=scripts;scripts",
        "--add-data=logs;logs",
        "--hidden-import=sqlite3",
        "--hidden-import=requests",
        "--hidden-import=urllib3",
        "--hidden-import=logging.handlers",
        "--runtime-hook=custom_runtime.py",
        # Protection options
        "--key=SmartAcademy2023!",  # Bytecode encryption key
        "--upx-dir=.",  # Use UPX if available
        "--strip",  # Strip symbols
        "--noupx",  # Don't use UPX (can be detected as malware)
    ]

    try:
        PyInstaller.__main__.run(pyinstaller_args)
    except Exception as e:
        print(f"PyInstaller build failed: {e}")
        print("Falling back to cx_Freeze...")
        build_with_cx_freeze()

def build_with_cx_freeze():
    """Fallback to cx_Freeze if PyInstaller fails"""
    print("Building with cx_Freeze...")
    subprocess.run([sys.executable, "setup.py", "build"], check=True)

def apply_post_build_protections():
    """Apply additional protections after build"""
    print("Applying post-build protections...")

    # 1. Add digital signature (requires signing certificate)
    # sign_executable()

    # 2. Add packer/compressor
    pack_executable()

    # 3. Add anti-tampering measures
    add_anti_tampering()

def pack_executable():
    """Pack executable with additional protectors"""
    exe_path = "dist/AdvancedBiometricApplication.exe"

    if os.path.exists(exe_path):
        print("Packing executable...")

        # Use UPX compression (optional)
        try:
            if shutil.which("upx"):
                subprocess.run(["upx", "--best", exe_path], check=True)
                print("UPX compression applied")
            else:
                print("UPX not available, skipping compression")
        except:
            print("UPX compression failed or skipped")

def add_anti_tampering():
    """Add anti-tampering measures"""
    print("Adding anti-tampering measures...")

    # Create a verification file
    verification_content = """
# Integrity verification data
# This file is used to verify the application hasn't been modified
import hashlib
import os
import sys

def verify_application_integrity():
    app_path = sys.argv[0]
    expected_hash = "your_application_hash_here"

    with open(app_path, 'rb') as f:
        actual_hash = hashlib.sha256(f.read()).hexdigest()

    return actual_hash == expected_hash

if not verify_application_integrity():
    print("Application integrity check failed!")
    sys.exit(1)
"""

    with open("integrity_check.py", "w") as f:
        f.write(verification_content)

def sign_executable():
    """Sign the executable (requires signing certificate)"""
    print("Note: Digital signing requires a code signing certificate.")
    print("You can obtain one from:")
    print("- DigiCert")
    print("- Sectigo")
    print("- GlobalSign")
    print("- Or use self-signed for testing")

    # Example signing command (would need actual certificate)
    # signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com dist/AdvancedBiometricApplication.exe

if __name__ == "__main__":
    build_protected_exe()
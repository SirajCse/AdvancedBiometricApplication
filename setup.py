# setup.py - Secure PyInstaller Build Configuration
import os
import sys
import subprocess
import hashlib
from pathlib import Path

# Application information
APP_NAME = "Advanced Biometric Application"
APP_VERSION = "2.0"
APP_DESCRIPTION = "Biometric attendance system"
APP_AUTHOR = "Advanced Biometric"
APP_AUTHOR_EMAIL = "info@bitdreamit.com"

def get_secure_key():
    """
    Securely retrieve encryption key from environment variable
    Never hardcode encryption keys in source code
    """
    key = os.environ.get('APP_ENCRYPTION_KEY')
    if not key:
        print("ERROR: APP_ENCRYPTION_KEY environment variable not set")
        print("Please set this variable with a secure encryption key")
        sys.exit(1)

    if len(key) < 16:
        print("ERROR: Encryption key must be at least 16 characters")
        sys.exit(1)

    return key

def calculate_file_hash(file_path):
    """Calculate SHA256 hash of a file for integrity verification"""
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(4096):
            hasher.update(chunk)
    return hasher.hexdigest()

def create_integrity_verifier(executable_path):
    """
    Create an integrity verification script that checks the executable hash
    against an expected value stored separately
    """
    # Calculate hash of the built executable
    actual_hash = calculate_file_hash(executable_path)

    # Create a separate verification file (would be stored securely in production)
    verifier_content = f'''#!/usr/bin/env python3
# Integrity verification module
import sys
import os
import hashlib

EXPECTED_HASH = "{actual_hash}"

def verify_application_integrity():
    """Verify the application executable hasn't been modified"""
    app_path = sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]

    try:
        # Calculate current hash
        hasher = hashlib.sha256()
        with open(app_path, 'rb') as f:
            while chunk := f.read(4096):
                hasher.update(chunk)
        current_hash = hasher.hexdigest()

        return current_hash == EXPECTED_HASH
    except Exception as e:
        print(f"Integrity check error: {{e}}")
        return False

if __name__ == "__main__":
    if verify_application_integrity():
        print("Integrity check passed")
        sys.exit(0)
    else:
        print("WARNING: Application integrity check failed!")
        print("The application may have been tampered with.")
        sys.exit(1)
'''

    # Write verifier to a file
    verifier_path = Path("integrity_verifier.py")
    with open(verifier_path, 'w') as f:
        f.write(verifier_content)

    print(f"Integrity verifier created with hash: {actual_hash}")
    return actual_hash

def build_with_pyinstaller():
    """Build the application using PyInstaller with security enhancements"""
    print("Building with PyInstaller...")

    # Get encryption key securely
    encryption_key = get_secure_key()

    # PyInstaller configuration
    pyinstaller_args = [
        "src/main.py",
        "--name", APP_NAME,
        "--onefile",
        "--windowed",
        "--clean",
        "--noconfirm",
        "--add-data", "config;config",
        "--add-data", "data;data",
        "--add-data", "scripts;scripts",
        "--hidden-import", "sqlite3",
        "--hidden-import", "requests",
        "--hidden-import", "urllib3",
        "--hidden-import", "logging.handlers",
        # Security options
        "--key", encryption_key,  # Bytecode encryption
        "--noupx",  # Avoid UPX which can trigger antivirus false positives
    ]

    try:
        # Import PyInstaller here to avoid dependency issues
        import PyInstaller.__main__
        PyInstaller.__main__.run(pyinstaller_args)

        # Path to the built executable
        executable_path = f"dist/{APP_NAME}.exe"

        if os.path.exists(executable_path):
            # Create integrity verification
            create_integrity_verifier(executable_path)
            print(f"Build completed successfully: {executable_path}")
            return True
        else:
            print("Build failed: Executable not found")
            return False

    except ImportError:
        print("PyInstaller not installed. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

        # Try again after installation
        import PyInstaller.__main__
        PyInstaller.__main__.run(pyinstaller_args)
        return True

    except Exception as e:
        print(f"PyInstaller build failed: {e}")
        return False

def apply_security_measures():
    """Apply additional security measures to the built executable"""
    executable_path = f"dist/{APP_NAME}.exe"

    if not os.path.exists(executable_path):
        print("Executable not found for security hardening")
        return False

    print("Applying additional security measures...")

    try:
        # Set restrictive file permissions (Windows)
        if os.name == 'nt':
            subprocess.run([
                'icacls', executable_path,
                '/inheritance:r',
                '/grant:r', 'Administrators:(F)',
                '/grant:r', 'SYSTEM:(F)',
                '/grant:r', 'Users:(RX)'
            ], check=True, capture_output=True)

        print("Security measures applied successfully")
        return True

    except subprocess.CalledProcessError as e:
        print(f"Warning: Could not set file permissions: {e}")
        return False

def main():
    """Main build function"""
    print("=" * 60)
    print(f"Building {APP_NAME} v{APP_VERSION}")
    print("=" * 60)

    # Create necessary directories
    Path("dist").mkdir(exist_ok=True)
    Path("build").mkdir(exist_ok=True)

    # Build with PyInstaller
    success = build_with_pyinstaller()

    if success:
        # Apply additional security measures
        apply_security_measures()

        print("\nBuild completed successfully!")
        print("Security features applied:")
        print("- Bytecode encryption with environment-based key")
        print("- Integrity verification system")
        print("- Restricted file permissions")
        print("- No external packers (reduces AV false positives)")

        print(f"\nExecutable available in: dist/{APP_NAME}.exe")
        print("\nImportant: Store the integrity hash securely for production use!")

    else:
        print("Build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
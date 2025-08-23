# check_structure.py
import os
from pathlib import Path

def check_structure():
    base_dir = Path("AdvancedBiometricApplication")
    required_files = [
        base_dir / "build_protected.py",
        base_dir / "install.bat",
        base_dir / "requirements.txt",
        base_dir / "setup.py",
        base_dir / "src" / "main.py",
        base_dir / "src" / "biometric" / "zk_device.py",
        base_dir / "src" / "core" / "database.py",
        base_dir / "src" / "utils" / "logger.py",
    ]

    missing_files = []
    for file_path in required_files:
        if not file_path.exists():
            missing_files.append(str(file_path))

    if missing_files:
        print("❌ Missing files:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    else:
        print("✅ All required files are present!")
        return True

if __name__ == "__main__":
    check_structure()
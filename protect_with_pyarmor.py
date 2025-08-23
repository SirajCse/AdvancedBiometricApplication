# protect_with_pyarmor.py
import os
import subprocess
import sys
from pathlib import Path

def protect_with_pyarmor():
    """Use PyArmor for professional code protection"""
    print("Protecting code with PyArmor...")

    try:
        # Install PyArmor if not already installed
        subprocess.run([sys.executable, "-m", "pip", "install", "pyarmor"], check=True)

        # Create PyArmor configuration
        config = """
# PyArmor configuration file
[package]
name = AdvancedBiometricApplication
output = dist

[options]
enable-suffix = 1
enable-jit = 1
mix-str = 1
obf-mod = 2
obf-code = 2
wrap-mode = 1
restrict-mode = 4

[runtime]
enable-bcc = 1
enable-rft = 1
enable-cross-protection = 1
        """

        with open('pyarmor.cfg', 'w') as f:
            f.write(config)

        # Run PyArmor protection
        cmd = [
            'pyarmor', 'gen',
            '--output', 'dist',
            '--package-runtime', '0',
            '--enable-suffix',
            '--enable-jit',
            '--mix-str',
            '--obf-mod', '2',
            '--obf-code', '2',
            '--wrap-mode', '1',
            '--restrict-mode', '4',
            '--enable-bcc',
            '--enable-rft',
            '--enable-cross-protection',
            'src/main.py'
        ]

        subprocess.run(cmd, check=True)
        print("PyArmor protection applied successfully!")

    except Exception as e:
        print(f"PyArmor protection failed: {e}")
        print("Falling back to standard protection...")
        return False

    return True

if __name__ == "__main__":
    protect_with_pyarmor()
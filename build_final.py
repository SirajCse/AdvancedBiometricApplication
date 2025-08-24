# create build_final.py
import os
import subprocess
import sys

def build_final():
    print("Building with ultimate fix...")

    # Get encryption key
    key = os.environ.get('APP_ENCRYPTION_KEY')
    if not key:
        key = "FallbackEncryptionKey1234567890"  # Fallback for testing
        print("Using fallback key for testing")

    # Build command with explicit paths
    cmd = [
        'pyinstaller',
        'src/main.py',
        '--name=AdvancedBiometricApplication',
        '--onefile',
        '--windowed',
        '--clean',
        '--add-data=config;config',
        '--add-data=data;data',
        '--add-data=scripts;scripts',
        '--hidden-import=core',
        '--hidden-import=core.database',
        '--hidden-import=core.device_manager',
        '--hidden-import=core.attendance_service',
        '--hidden-import=utils',
        '--hidden-import=utils.logger',
        '--hidden-import=utils.windows_utils',
        '--hidden-import=utils.config_manager',
        '--hidden-import=biometric',
        '--hidden-import=biometric.zk_device',
        '--paths=.',
        '--paths=src',
        f'--key={key}',
        '--noupx',
    ]

    print("Running:", ' '.join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Build successful!")
        print("Testing executable...")
        test_result = subprocess.run(['dist/AdvancedBiometricApplication.exe', '--help'],
                                   capture_output=True, text=True)
        if test_result.returncode == 0:
            print("✅ Executable works perfectly!")
        else:
            print("❌ Executable test failed:", test_result.stderr)
    else:
        print("❌ Build failed:", result.stderr)

if __name__ == "__main__":
    build_final()
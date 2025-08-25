@echo off
echo Advanced Biometric Application - License Activation
echo ==================================================

python -c "
import sys
sys.path.insert(0, '.')
from src.utils.license_manager import LicenseManager

print('License Activation')
print('=================')
print('')

license_key = input('Enter your license key: ').strip()

manager = LicenseManager()
success, message = manager.activate_license(license_key)

if success:
    print('✅ ' + message)
    print('')
    print('License Information:')
    print('====================')
    info = manager.get_license_info()
    for key, value in info.items():
        if key != 'license_key':  # Don't show full key
            print(f'{key}: {value}')
else:
    print('❌ ' + message)

print('')
input('Press Enter to continue...')
"
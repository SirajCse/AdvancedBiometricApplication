# src/utils/license_manager.py
import hashlib
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

class LicenseManager:
    def __init__(self, license_file="config/license.json"):
        self.license_file = Path(license_file)
        self.license_data = self.load_license()

    def load_license(self):
        """Load license data from file"""
        if self.license_file.exists():
            try:
                with open(self.license_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load license file: {e}")
                return {}
        return {}

    def save_license(self):
        """Save license data to file"""
        try:
            self.license_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.license_file, 'w') as f:
                json.dump(self.license_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving license: {e}")
            return False

    def generate_license(self, customer_name, device_count, days_valid=365):
        """Generate a new license key"""
        license_key = self._generate_key(customer_name, device_count)

        self.license_data = {
            "license_key": license_key,
            "customer_name": customer_name,
            "device_count": device_count,
            "max_devices": device_count,  # Maximum allowed devices
            "issued_date": datetime.now().isoformat(),
            "expiry_date": (datetime.now() + timedelta(days=days_valid)).isoformat(),
            "valid_days": days_valid,
            "activated": False,
            "version": "1.0"
        }

        self.save_license()
        return license_key

    def _generate_key(self, customer_name, device_count):
        """Generate a unique license key"""
        secret_salt = os.environ.get('LICENSE_SALT', 'DefaultBiometricSalt2024')
        base_string = f"{customer_name}{device_count}{secret_salt}{datetime.now().timestamp()}"
        return hashlib.sha512(base_string.encode()).hexdigest()[:32].upper()

    def validate_license(self):
        """Validate the current license"""
        if not self.license_data:
            return False, "No license found"

        # Check if activated
        if not self.license_data.get('activated', False):
            return False, "License not activated"

        # Check expiry
        expiry_str = self.license_data.get('expiry_date')
        if expiry_str:
            try:
                expiry_date = datetime.fromisoformat(expiry_str)
                if datetime.now() > expiry_date:
                    return False, "License expired"
            except:
                return False, "Invalid expiry date format"

        return True, "License valid"

    def activate_license(self, activation_key):
        """Activate the license with a key"""
        stored_key = self.license_data.get('license_key')
        if stored_key and stored_key == activation_key:
            self.license_data['activated'] = True
            self.license_data['activation_date'] = datetime.now().isoformat()
            self.save_license()
            return True, "License activated successfully"
        return False, "Invalid activation key"

    def get_license_info(self):
        """Get license information for display"""
        return self.license_data.copy()

# Utility function for easy access
def get_license_manager():
    return LicenseManager()
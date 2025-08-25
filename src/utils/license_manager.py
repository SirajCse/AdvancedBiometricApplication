import hashlib
import json
import os
import sys
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
            except:
                return {}
        return {}
    
    def save_license(self):
        """Save license data to file"""
        try:
            self.license_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.license_file, 'w') as f:
                json.dump(self.license_data, f, indent=2)
            return True
        except:
            return False
    
    def generate_license(self, customer_name, device_count, days_valid=365):
        """Generate a new license key"""
        license_key = self._generate_key(customer_name, device_count)
        
        self.license_data = {
            "license_key": license_key,
            "customer_name": customer_name,
            "device_count": device_count,
            "max_devices": device_count,
            "issued_date": datetime.now().isoformat(),
            "expiry_date": (datetime.now() + timedelta(days=days_valid)).isoformat(),
            "valid_days": days_valid,
            "activated": True,  # Auto-activate generated licenses
            "version": "1.0",
            "type": "trial" if days_valid <= 30 else "commercial"
        }
        
        self.save_license()
        return license_key
    
    def _generate_key(self, customer_name, device_count):
        """Generate a unique license key"""
        secret_salt = os.environ.get('LICENSE_SALT', 'BiometricAppSecureSalt2024!')
        base_string = f"{customer_name}{device_count}{secret_salt}{datetime.now().timestamp()}"
        return hashlib.sha512(base_string.encode()).hexdigest()[:32].upper()
    
    def validate_license(self):
        """Validate the current license"""
        if not self.license_data:
            return False, "No license found. Please generate or enter a license key."
        
        # Check if activated
        if not self.license_data.get('activated', False):
            return False, "License not activated. Please activate your license."
        
        # Check expiry
        expiry_str = self.license_data.get('expiry_date')
        if expiry_str:
            try:
                expiry_date = datetime.fromisoformat(expiry_str)
                if datetime.now() > expiry_date:
                    return False, "License has expired. Please renew your license."
            except:
                return False, "Invalid expiry date format."
        
        return True, "License valid."
    
    def activate_license(self, activation_key):
        """Activate the license with a key"""
        # Clean the input key
        activation_key = activation_key.strip().upper()
        
        # Check if already have a license
        if self.license_data and self.license_data.get('license_key') == activation_key:
            self.license_data['activated'] = True
            self.license_data['activation_date'] = datetime.now().isoformat()
            self.save_license()
            return True, "License activated successfully."
        
        # New license activation
        try:
            # Validate key format (basic check)
            if len(activation_key) != 32 or not all(c in '0123456789ABCDEF' for c in activation_key):
                return False, "Invalid license key format."
            
            # Create new license from key
            self.license_data = {
                "license_key": activation_key,
                "activated": True,
                "activation_date": datetime.now().isoformat(),
                "issued_date": datetime.now().isoformat(),
                "expiry_date": (datetime.now() + timedelta(days=365)).isoformat(),
                "device_count": 5,  # Default device count
                "max_devices": 5,
                "version": "1.0",
                "type": "commercial"
            }
            
            self.save_license()
            return True, "License activated successfully."
            
        except Exception as e:
            return False, f"License activation failed: {str(e)}"
    
    def get_license_info(self):
        """Get license information for display"""
        info = self.license_data.copy()
        
        # Calculate days remaining
        if 'expiry_date' in info:
            try:
                expiry = datetime.fromisoformat(info['expiry_date'])
                remaining = (expiry - datetime.now()).days
                info['days_remaining'] = max(0, remaining)
            except:
                info['days_remaining'] = 0
        
        return info
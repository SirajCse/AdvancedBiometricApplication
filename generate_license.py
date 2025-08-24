# generate_license.py
import sys
import os
from pathlib import Path

# Add the parent directory to Python path to import your modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def generate_license():
    """Interactive license key generation script"""
    print("=" * 50)
    print("Advanced Biometric Application - License Generator")
    print("=" * 50)

    try:
        # Try to import the LicenseManager
        from src.utils.license_manager import LicenseManager

        # Get user input
        print("\nPlease enter license details:")
        customer_name = input("Customer Name/Email: ").strip()

        while True:
            try:
                device_count = int(input("Number of Devices: ").strip())
                if device_count > 0:
                    break
                else:
                    print("Please enter a positive number.")
            except ValueError:
                print("Please enter a valid number.")

        while True:
            try:
                days_valid = int(input("Days Valid (365 for 1 year): ").strip())
                if days_valid > 0:
                    break
                else:
                    print("Please enter a positive number.")
            except ValueError:
                print("Please enter a valid number.")

        # Generate license
        manager = LicenseManager()
        license_key = manager.generate_license(customer_name, device_count, days_valid)

        print("\n" + "=" * 50)
        print("✅ LICENSE GENERATED SUCCESSFULLY!")
        print("=" * 50)
        print(f"Customer: {customer_name}")
        print(f"Devices: {device_count}")
        print(f"Valid for: {days_valid} days")
        print(f"License Key: {license_key}")
        print("\n📋 License file saved to: config/license.json")
        print("\n⚠️  Important: Share this license key with the customer.")
        print("They need to activate it using the activation command.")

    except ImportError as e:
        print(f"❌ Error: Could not import LicenseManager")
        print(f"Make sure the file src/utils/license_manager.py exists")
        print(f"Error details: {e}")

    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def show_license_info():
    """Show current license information"""
    try:
        from src.utils.license_manager import LicenseManager

        manager = LicenseManager()

        if manager.license_data:
            print("\n📄 CURRENT LICENSE INFORMATION:")
            print("=" * 40)
            for key, value in manager.license_data.items():
                if key not in ['license_key']:  # Don't show full key by default
                    print(f"{key.replace('_', ' ').title()}: {value}")

            # Show partial license key for verification
            if 'license_key' in manager.license_data:
                license_key = manager.license_data['license_key']
                print(f"License Key: {license_key[:8]}...{license_key[-8:]}")
        else:
            print("No license file found. Generate a license first.")

    except ImportError:
        print("License manager not available")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "info":
        show_license_info()
    else:
        generate_license()
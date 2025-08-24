# test_device.py
import sys
import os
from pathlib import Path

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, str(Path(__file__).parent))

from src.biometric.zk_device import ZKDevice

def test_device_connection():
    """Test connection to ZKTeco device"""
    print("Testing ZKTeco device connection...")

    # Test configuration - replace with your actual device IP
    test_config = {
        "ip": "192.168.1.201",
        "port": 4370,
        "serial_number": "TEST_DEVICE",
        "name": "Test Device",
        "enabled": True,
        "timeout": 10
    }

    try:
        device = ZKDevice(
            ip=test_config['ip'],
            port=test_config['port'],
            serial_number=test_config['serial_number'],
            timeout=test_config['timeout']
        )

        print(f"Connecting to {test_config['ip']}:{test_config['port']}...")

        if device.connect():
            print("✅ Connection successful!")

            # Try to get device info
            info = device.get_device_info()
            if info:
                print(f"Device Info: {info}")
            else:
                print("⚠️  Could not retrieve device info")

            device.disconnect()
            return True
        else:
            print("❌ Connection failed")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_device_connection()
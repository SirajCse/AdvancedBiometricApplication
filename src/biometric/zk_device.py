# src/biometric/zk_device.py
import socket
import threading
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional, Generator

from src.biometric.zk_lib.base import ZK
from src.biometric.zk_lib.attendance import Attendance

logger = logging.getLogger(__name__)

class ZKDevice:
    def __init__(self, ip: str, port: int = 4370, serial_number: str = None, timeout: int = 30):
        self.ip = ip
        self.port = port
        self.serial_number = serial_number
        self.timeout = timeout
        self.zk_client = None
        self.is_connected_flag = False
        self.lock = threading.RLock()

    def connect(self, timeout: int = None) -> bool:
        """Connect to the device using the ZK library"""
        if timeout is None:
            timeout = self.timeout

        with self.lock:
            try:
                if self.is_connected():
                    return True

                self.zk_client = ZK(
                    ip=self.ip,
                    port=self.port,
                    timeout=timeout,
                    ommit_ping=True
                )

                if self.zk_client.connect():
                    self.is_connected_flag = True
                    logger.info(f"Connected to device {self.serial_number or self.ip}")
                    return True

            except Exception as e:
                logger.error(f"Connection failed to {self.ip}:{self.port}: {e}")
                self.disconnect()

            return False

    def disconnect(self):
        """Disconnect from the device"""
        with self.lock:
            if self.zk_client:
                try:
                    self.zk_client.disconnect()
                except Exception as e:
                    logger.error(f"Error disconnecting: {e}")
                finally:
                    self.zk_client = None
            self.is_connected_flag = False

    def is_connected(self) -> bool:
        """Check if connected to the device"""
        return self.is_connected_flag and self.zk_client is not None

    def get_live_attendance(self) -> List[Dict]:
        """Get live attendance data using ZK library"""
        if not self.is_connected():
            return []

        try:
            attendance_data = []
            records = self.zk_client.get_attendance()

            for record in records:
                attendance_data.append({
                    'user_id': record.user_id,
                    'timestamp': record.timestamp,
                    'status': record.status,
                    'punch': record.punch
                })

            return attendance_data
        except Exception as e:
            logger.error(f"Error getting attendance from device {self.serial_number}: {e}")
            return []

    def live_capture(self) -> Generator[Dict, None, None]:
        """Live capture of attendance events using ZK library"""
        if not self.is_connected():
            return

        try:
            for attendance in self.zk_client.live_capture():
                if attendance:
                    yield {
                        'user_id': attendance.user_id,
                        'timestamp': attendance.timestamp,
                        'status': attendance.status,
                        'punch': attendance.punch
                    }
        except Exception as e:
            logger.error(f"Error in live capture for device {self.serial_number}: {e}")

    def get_device_info(self) -> Optional[Dict]:
        """Get device information"""
        if not self.is_connected():
            return None

        try:
            device_time = self.zk_client.get_time()

            return {
                'serial_number': self.serial_number or 'Unknown',
                'ip_address': self.ip,
                'device_time': device_time.isoformat() if device_time else 'Unknown',
                'platform': 'ZK Device',
                'device_name': f'ZK Device {self.ip}'
            }
        except Exception as e:
            logger.error(f"Error getting device info: {e}")
            return None

    def sync_time(self) -> bool:
        """Synchronize device time with system time"""
        if not self.is_connected():
            return False

        try:
            return self.zk_client.set_time(datetime.now())
        except Exception as e:
            logger.error(f"Error syncing time with device {self.serial_number}: {e}")
            return False

    def clear_attendance_log(self) -> bool:
        """Clear attendance log on device"""
        if not self.is_connected():
            return False

        try:
            return self.zk_client.clear_attendance()
        except Exception as e:
            logger.error(f"Error clearing attendance log on device {self.serial_number}: {e}")
            return False

    def get_users(self) -> List[Dict]:
        """Get users from device"""
        if not self.is_connected():
            return []

        try:
            users = self.zk_client.get_users()
            return [
                {
                    'uid': user.uid,
                    'name': user.name,
                    'privilege': user.privilege,
                    'user_id': user.user_id
                }
                for user in users
            ]
        except Exception as e:
            logger.error(f"Error getting users from device {self.serial_number}: {e}")
            return []
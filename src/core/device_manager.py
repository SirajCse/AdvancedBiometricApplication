# src/core/device_manager.py
import threading
import time
import logging
from typing import Dict, List, Optional
from queue import Queue

from src.biometric.zk_device import ZKDevice
from src.core.database import DatabaseManager

logger = logging.getLogger(__name__)

class DeviceManager:

    def __init__(self, db_manager: DatabaseManager, config: Dict = None):
        self.db = db_manager
        self.config = config or {}
        self.devices: Dict[str, ZKDevice] = {}
        self.attendance_queue = Queue()
        self.is_running = False
        self.thread = None
        self.live_capture_threads = {}

    # Update initialize_devices method:
    def initialize_devices(self, devices_config: List[Dict] = None):
        """Initialize all configured devices using ZK library"""
        if devices_config is None:
            devices_config = self.config.get('devices', [])

        for device_info in devices_config:
            try:
                device = ZKDevice(
                    ip=device_info['ip'],
                    port=device_info.get('port', 4370),
                    serial_number=device_info.get('serial_number'),
                    timeout=device_info.get('timeout', 30)
                )
                if device.connect():
                    self.devices[device_info.get('serial_number', device_info['ip'])] = device
                    logger.info(f"Connected to device {device_info.get('serial_number', device_info['ip'])} at {device_info['ip']}")

                    # Sync device time if enabled
                    if device_info.get('sync_time', True):
                        if device.sync_time():
                            logger.info(f"Synchronized time with device {device_info.get('serial_number', device_info['ip'])}")

                else:
                    logger.error(f"Failed to connect to device {device_info.get('serial_number', device_info['ip'])}")
            except Exception as e:
                logger.error(f"Error initializing device {device_info.get('serial_number', device_info['ip'])}: {e}")

    def start_live_capture(self):
        """Start live capture on all devices"""
        if not self.is_running:
            self.is_running = True

            for serial_number, device in self.devices.items():
                thread = threading.Thread(
                    target=self._live_capture_loop,
                    args=(device,),
                    daemon=True,
                    name=f"LiveCapture-{serial_number}"
                )
                self.live_capture_threads[serial_number] = thread
                thread.start()

            logger.info("Started live capture on all devices")

    def stop_live_capture(self):
        """Stop live capture on all devices"""
        self.is_running = False

        for thread in self.live_capture_threads.values():
            thread.join(timeout=5.0)

        self.live_capture_threads.clear()
        logger.info("Stopped live capture on all devices")

    def _live_capture_loop(self, device: ZKDevice):
        """Live capture loop for a single device"""
        while self.is_running:
            try:
                if not device.is_connected():
                    device.connect()

                # Use the ZK library's live capture functionality
                for attendance in device.live_capture():
                    if attendance:
                        # Add to processing queue
                        self.attendance_queue.put({
                            'user_id': attendance['user_id'],
                            'punch_time': attendance['timestamp'].isoformat(),
                            'device_ip': device.ip,
                            'device_sn': device.serial_number,
                            'status': attendance['status'],
                            'punch': attendance['punch']
                        })

            except Exception as e:
                logger.error(f"Error in live capture for device {device.serial_number}: {e}")
                time.sleep(5)  # Wait before retrying

    def process_attendance_queue(self):
        """Process attendance records from the queue"""
        processed_records = []

        while not self.attendance_queue.empty():
            try:
                record = self.attendance_queue.get_nowait()
                success = self.db.insert_attendance(
                    user_id=record['user_id'],
                    punch_time=record['punch_time'],
                    device_ip=record['device_ip'],
                    device_sn=record['device_sn']
                )

                if success:
                    processed_records.append(record)
                    logger.info(f"Recorded attendance for user {record['user_id']} from device {record['device_sn']}")

                self.attendance_queue.task_done()
            except Exception as e:
                logger.error(f"Error processing attendance record: {e}")

        return processed_records

    def get_device_status(self, serial_number: str) -> Optional[Dict]:
        """Get status of a specific device"""
        device = self.devices.get(serial_number)
        if not device:
            return None

        try:
            info = device.get_device_info()
            return {
                'connected': device.is_connected(),
                'info': info,
                'serial_number': serial_number
            }
        except Exception as e:
            logger.error(f"Error getting status for device {serial_number}: {e}")
            return None

    def get_all_devices_status(self) -> List[Dict]:
        """Get status of all devices"""
        status_list = []
        for serial_number in self.devices.keys():
            status = self.get_device_status(serial_number)
            if status:
                status_list.append(status)
        return status_list

    def disconnect_all(self):
        """Disconnect all devices"""
        self.stop_live_capture()

        for device in self.devices.values():
            try:
                device.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting device: {e}")
        
        self.devices.clear()
        logger.info("Disconnected all devices")
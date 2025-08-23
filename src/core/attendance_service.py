# src/core/attendance_service.py
import threading
import time
import logging
import requests
from typing import List, Dict, Optional
from datetime import datetime

from .database import DatabaseManager
from .device_manager import DeviceManager

logger = logging.getLogger(__name__)

class AttendanceService:
    def __init__(self, db_manager, device_manager, config=None):
        self.db = db_manager
        self.device_manager = device_manager
        self.config = config or {}
        self.is_running = False
        self.sync_thread = None
        self.sync_interval = self.config.get('sync', {}).get('interval_seconds', 300)
        
    def start(self, sync_config: Dict = None):
        """Start the attendance synchronization service"""
        if sync_config is None:
            sync_config = self.config.get('sync', {})

        if self.is_running:
            return

        self.is_running = True
        self.sync_interval = int(sync_config.get('interval_seconds', 300))
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()
        logger.info("Attendance service started")
        
    def stop(self):
        """Stop the attendance synchronization service"""
        self.is_running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=5.0)
        logger.info("Attendance service stopped")
        
    def _sync_loop(self):
        """Main synchronization loop"""
        while self.is_running:
            try:
                # Process any new attendance records from devices
                self.device_manager.process_attendance_queue()
                
                # Sync attendance with server
                self.sync_attendance()
                
                # Wait for next sync cycle
                time.sleep(self.sync_interval)
                
            except Exception as e:
                logger.error(f"Error in sync loop: {e}")
                time.sleep(60)  # Wait longer on error
    
    def sync_attendance(self):
        """Sync attendance records with the server"""
        site_url = self.db.get_config_value('site_url', '')
        if not site_url or site_url == 'enter your Website URL':
            logger.warning("Site URL not configured, skipping sync")
            return
            
        # Get unsynced attendance records
        unsynced_records = self.db.get_unsynced_attendance()
        if not unsynced_records:
            return
            
        successful_syncs = []
        
        for record in unsynced_records:
            try:
                # Prepare data for server
                json_data = {
                    'uid': record['UserID'],
                    'user_id': record['UserID'],
                    't': record['PunchDateTime'],
                    'ip': record['IPAddr'],
                    'serial_number': record['SrNo']
                }
                
                # Send to server
                response = requests.post(
                    f"{site_url}biometric",
                    json=json_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    successful_syncs.append(record['ID'])
                    logger.info(f"Synced attendance record {record['ID']} for user {record['UserID']}")
                else:
                    logger.warning(f"Server rejected attendance record {record['ID']}: {response.status_code}")
                    
            except requests.RequestException as e:
                logger.error(f"Network error syncing record {record['ID']}: {e}")
            except Exception as e:
                logger.error(f"Error syncing record {record['ID']}: {e}")
        
        # Mark successfully synced records
        if successful_syncs:
            self.db.mark_attendance_synced(successful_syncs)
            logger.info(f"Marked {len(successful_syncs)} records as synced")
    
    def get_sync_status(self) -> Dict:
        """Get synchronization status"""
        unsynced = self.db.get_unsynced_attendance()
        return {
            'unsynced_count': len(unsynced),
            'sync_interval': self.sync_interval,
            'last_sync': datetime.now().isoformat()  # Would be stored in DB in real implementation
        }
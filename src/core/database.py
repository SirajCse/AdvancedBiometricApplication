# src/core/database.py
import sqlite3
import json
import logging
from typing import Optional, List, Tuple, Any, Dict
from pathlib import Path

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "data/att.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection with proper settings"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        return conn

    def _init_database(self):
        """Initialize database tables"""
        tables = {
            "devices": """
                CREATE TABLE IF NOT EXISTS devices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip TEXT NOT NULL,
                    port INTEGER DEFAULT 4370,
                    serial_number TEXT NOT NULL UNIQUE,
                    name TEXT,
                    last_sync TIMESTAMP,
                    is_active INTEGER DEFAULT 1
                )
            """,
            "attendance": """
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    punch_time TIMESTAMP NOT NULL,
                    device_ip TEXT,
                    device_sn TEXT,
                    status TEXT DEFAULT 'pending',
                    sync_time TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            "configuration": """
                CREATE TABLE IF NOT EXISTS configuration (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """,
            "users": """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    name TEXT,
                    privilege INTEGER,
                    password TEXT,
                    last_updated TIMESTAMP
                )
            """
        }

        with self._get_connection() as conn:
            for table_name, table_sql in tables.items():
                try:
                    conn.execute(table_sql)
                except sqlite3.Error as e:
                    logger.error(f"Error creating table {table_name}: {e}")

            # Insert default configuration if not exists
            #""" ENVIRONMENT """
            default_config = {
                "site_url": "https://your-academy.example.com/",
                "sync_interval": "300",
                "auto_start": "1",
                "log_level": "INFO"
            }

            for key, value in default_config.items():
                conn.execute(
                    "INSERT OR IGNORE INTO configuration (key, value) VALUES (?, ?)",
                    (key, value)
                )

            conn.commit()

    def execute_query(self, query: str, params: tuple = None, commit: bool = False) -> Optional[sqlite3.Cursor]:
        """Execute a SQL query with error handling"""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(query, params or ())
                if commit:
                    conn.commit()
                return cursor
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            return None

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        cursor = self.execute_query("SELECT value FROM configuration WHERE key = ?", (key,))
        result = cursor.fetchone() if cursor else None
        return result[0] if result else default

    def set_config_value(self, key: str, value: Any) -> bool:
        """Set a configuration value"""
        cursor = self.execute_query(
            "INSERT OR REPLACE INTO configuration (key, value) VALUES (?, ?)",
            (key, str(value)),
            commit=True
        )
        return cursor is not None

    # Device management methods
    def get_devices(self) -> List[Dict]:
        """Get all active devices"""
        cursor = self.execute_query(
            "SELECT id, ip, port, serial_number, name, last_sync FROM devices WHERE is_active = 1"
        )
        if cursor:
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        return []

    def add_device(self, ip: str, port: int, serial_number: str, name: str = None) -> bool:
        """Add a new device"""
        cursor = self.execute_query(
            "INSERT OR REPLACE INTO devices (ip, port, serial_number, name) VALUES (?, ?, ?, ?)",
            (ip, port, serial_number, name),
            commit=True
        )
        return cursor is not None and cursor.rowcount > 0

    def delete_device(self, serial_number: str) -> bool:
        """Delete a device"""
        cursor = self.execute_query(
            "DELETE FROM devices WHERE serial_number = ?",
            (serial_number,),
            commit=True
        )
        return cursor is not None and cursor.rowcount > 0

    # Attendance methods
    def insert_attendance(self, user_id: int, punch_time: str, device_ip: str, device_sn: str) -> bool:
        """Insert attendance record"""
        cursor = self.execute_query(
            """INSERT INTO attendance (user_id, punch_time, device_ip, device_sn)
               VALUES (?, ?, ?, ?)""",
            (user_id, punch_time, device_ip, device_sn),
            commit=True
        )
        return cursor is not None and cursor.rowcount > 0

    def get_unsynced_attendance(self, limit: int = 100) -> List[Dict]:
        """Get unsynced attendance records"""
        cursor = self.execute_query(
            "SELECT * FROM attendance WHERE status = 'pending' ORDER BY punch_time LIMIT ?",
            (limit,)
        )
        if cursor:
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        return []

    def mark_attendance_synced(self, attendance_ids: List[int]) -> bool:
        """Mark attendance records as synced"""
        if not attendance_ids:
            return True

        placeholders = ','.join('?' * len(attendance_ids))
        cursor = self.execute_query(
            f"UPDATE attendance SET status = 'synced', sync_time = CURRENT_TIMESTAMP WHERE id IN ({placeholders})",
            attendance_ids,
            commit=True
        )
        return cursor is not None
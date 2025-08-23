# src/core/database.py
from __future__ import annotations

import sqlite3
import json
import logging
import time
from typing import Optional, List, Tuple, Any, Dict, Iterable, Callable
from pathlib import Path
from contextlib import contextmanager

logger = logging.getLogger(__name__)

_LOCKED_ERRORS = ("database is locked", "database table is locked")

class DatabaseManager:
    def __init__(self, db_path: str = "data/att.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    # ---------- Connection Management ----------

    def _connect(self) -> sqlite3.Connection:
        """
        Fresh connection per operation. Safe for threads/processes.
        """
        conn = sqlite3.connect(
            self.db_path,
            detect_types=sqlite3.PARSE_DECLTYPES,
            isolation_level="DEFERRED",  # transactional by default
        )
        conn.row_factory = sqlite3.Row
        # Pragmas tuned for service workloads
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.execute("PRAGMA temp_store = MEMORY")
        conn.execute("PRAGMA busy_timeout = 5000")  # ms
        return conn

    @contextmanager
    def _conn_ctx(self) -> Iterable[sqlite3.Connection]:
        conn = self._connect()
        try:
            yield conn
            # Let caller decide commits; but most ops use _execute(..., commit=True)
        finally:
            conn.close()

    # ---------- Initialization & Migrations ----------

    def _init_database(self) -> None:
        with self._conn_ctx() as conn:
            # schema_version tracking
            conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    version INTEGER NOT NULL
                )
            """)
            # v1 schema (your original tables, slightly hardened)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS devices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip TEXT NOT NULL,
                    port INTEGER DEFAULT 4370,
                    serial_number TEXT NOT NULL UNIQUE,
                    name TEXT,
                    last_sync TIMESTAMP,
                    is_active INTEGER DEFAULT 1 CHECK (is_active IN (0,1))
                )
            """)
            conn.execute("""
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
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS configuration (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    name TEXT,
                    privilege INTEGER,
                    password TEXT,
                    last_updated TIMESTAMP
                )
            """)

            # Indexes for performance & dedup
            conn.execute("CREATE INDEX IF NOT EXISTS idx_devices_active ON devices(is_active)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_attendance_status ON attendance(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_attendance_punchtime ON attendance(punch_time)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_attendance_user_time ON attendance(user_id, punch_time)")
            # Soft uniqueness to prevent duplicate punches (same user, time, device)
            conn.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS ux_attendance_user_time_device
                ON attendance(user_id, punch_time, device_sn)
            """)

            # Default config
            defaults = {
                "site_url": "https://your-academy.example.com/",
                "sync_interval": "300",
                "auto_start": "1",
                "log_level": "INFO",
            }
            for k, v in defaults.items():
                conn.execute(
                    "INSERT OR IGNORE INTO configuration (key, value) VALUES (?, ?)",
                    (k, v),
                )

            # Initialize schema version if missing
            cur = conn.execute("SELECT version FROM schema_version WHERE id = 1")
            row = cur.fetchone()
            if not row:
                conn.execute("INSERT INTO schema_version (id, version) VALUES (1, 1)")

            conn.commit()

        # Future migrations handled here
        self._migrate()

    def _migrate(self) -> None:
        """Apply forward-only migrations if schema_version < latest."""
        latest = 1
        with self._conn_ctx() as conn:
            version = conn.execute(
                "SELECT version FROM schema_version WHERE id = 1"
            ).fetchone()[0]
            # Example future migration template:
            # if version < 2:
            #     conn.execute("ALTER TABLE ...")
            #     conn.execute("UPDATE schema_version SET version = 2 WHERE id = 1")
            #     conn.commit()
            if version != latest:
                conn.execute("UPDATE schema_version SET version = ? WHERE id = 1", (latest,))
                conn.commit()

    # ---------- Low-level Execute with Retries ----------

    def _execute(
        self,
        sql: str,
        params: Tuple[Any, ...] | List[Any] | None = None,
        *,
        commit: bool = False,
        many: bool = False,
        seq_of_params: Iterable[Tuple[Any, ...]] | None = None,
        max_retries: int = 5,
        base_sleep: float = 0.05,
    ) -> Optional[sqlite3.Cursor]:
        attempt = 0
        while True:
            try:
                with self._conn_ctx() as conn:
                    cur = conn.cursor()
                    if many and seq_of_params is not None:
                        cur.executemany(sql, seq_of_params)
                    else:
                        cur.execute(sql, params or [])
                    if commit:
                        conn.commit()
                    return cur
            except sqlite3.OperationalError as e:
                msg = str(e).lower()
                if any(lock_msg in msg for lock_msg in _LOCKED_ERRORS) and attempt < max_retries:
                    sleep = base_sleep * (2 ** attempt)
                    logger.warning(f"SQLite locked, retrying in {sleep:.3f}s (attempt {attempt+1}/{max_retries})")
                    time.sleep(sleep)
                    attempt += 1
                    continue
                logger.error(f"Database operational error: {e} | SQL: {sql} | params: {params}")
                return None
            except sqlite3.Error as e:
                logger.error(f"Database error: {e} | SQL: {sql} | params: {params}")
                return None

    # ---------- Config Helpers (string & JSON) ----------

    def get_config_value(self, key: str, default: Any = None) -> Any:
        cur = self._execute("SELECT value FROM configuration WHERE key = ?", (key,))
        row = cur.fetchone() if cur else None
        return row["value"] if row else default

    def set_config_value(self, key: str, value: Any) -> bool:
        return self._execute(
            "INSERT OR REPLACE INTO configuration (key, value) VALUES (?, ?)",
            (key, str(value)),
            commit=True,
        ) is not None

    def get_config_json(self, key: str, default: Any = None) -> Any:
        val = self.get_config_value(key)
        if val is None:
            return default
        try:
            return json.loads(val)
        except json.JSONDecodeError:
            return default

    def set_config_json(self, key: str, value: Any) -> bool:
        return self.set_config_value(key, json.dumps(value, separators=(",", ":")))

    # ---------- Devices ----------

    def get_devices(self) -> List[Dict[str, Any]]:
        cur = self._execute(
            "SELECT id, ip, port, serial_number, name, last_sync FROM devices WHERE is_active = 1"
        )
        return [dict(row) for row in cur.fetchall()] if cur else []

    def add_device(self, ip: str, port: int, serial_number: str, name: Optional[str] = None) -> bool:
        cur = self._execute(
            "INSERT OR REPLACE INTO devices (ip, port, serial_number, name) VALUES (?, ?, ?, ?)",
            (ip, port, serial_number, name),
            commit=True,
        )
        return bool(cur and cur.rowcount > 0)

    def delete_device(self, serial_number: str) -> bool:
        cur = self._execute(
            "DELETE FROM devices WHERE serial_number = ?",
            (serial_number,),
            commit=True,
        )
        return bool(cur and cur.rowcount > 0)

    # ---------- Attendance ----------

    def insert_attendance(self, user_id: int, punch_time: str, device_ip: str, device_sn: str) -> bool:
        """
        Insert attendance; duplicates (same user, time, device) are ignored by unique index.
        Returns True if inserted, False if duplicate or failure.
        """
        cur = self._execute(
            """
            INSERT OR IGNORE INTO attendance (user_id, punch_time, device_ip, device_sn)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, punch_time, device_ip, device_sn),
            commit=True,
        )
        return bool(cur and cur.rowcount > 0)

    def bulk_insert_attendance(self, rows: List[Tuple[int, str, str, str]]) -> int:
        """
        Efficient batch insert with IGNORE semantics.
        rows = [(user_id, punch_time, device_ip, device_sn), ...]
        Returns number of rows inserted (duplicates ignored).
        """
        cur_before = self._execute("SELECT changes()", ())
        before = cur_before.fetchone()[0] if cur_before else 0
        cur = self._execute(
            "INSERT OR IGNORE INTO attendance (user_id, punch_time, device_ip, device_sn) VALUES (?, ?, ?, ?)",
            many=True,
            seq_of_params=rows,
            commit=True,
        )
        cur_after = self._execute("SELECT changes()", ())
        after = cur_after.fetchone()[0] if cur_after else 0
        return max(0, after - before)

    def get_unsynced_attendance(self, limit: int = 100) -> List[Dict[str, Any]]:
        cur = self._execute(
            """
            SELECT *
            FROM attendance
            WHERE status = 'pending'
            ORDER BY punch_time
            LIMIT ?
            """,
            (limit,),
        )
        return [dict(row) for row in cur.fetchall()] if cur else []

    def mark_attendance_synced(self, attendance_ids: List[int]) -> bool:
        if not attendance_ids:
            return True
        placeholders = ",".join("?" * len(attendance_ids))
        cur = self._execute(
            f"UPDATE attendance SET status = 'synced', sync_time = CURRENT_TIMESTAMP WHERE id IN ({placeholders})",
            attendance_ids,
            commit=True,
        )
        return bool(cur)

    # ---------- Users (optional helpers) ----------

    def upsert_user(self, user_id: int, name: Optional[str], privilege: Optional[int], password: Optional[str]) -> bool:
        cur = self._execute(
            """
            INSERT INTO users (user_id, name, privilege, password, last_updated)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                name=excluded.name,
                privilege=excluded.privilege,
                password=excluded.password,
                last_updated=CURRENT_TIMESTAMP
            """,
            (user_id, name, privilege, password),
            commit=True,
        )
        return bool(cur)

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        cur = self._execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone() if cur else None
        return dict(row) if row else None

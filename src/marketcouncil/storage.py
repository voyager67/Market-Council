"""SQLite persistence, append-only audit events, and tenant-scoped records."""

from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'trader' CHECK(role IN ('trader','admin')),
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sessions (
    token_hash TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    revoked_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
CREATE TABLE IF NOT EXISTS audit_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL REFERENCES users(id),
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_audit_user_created ON audit_events(user_id, created_at);
CREATE TRIGGER IF NOT EXISTS audit_events_no_update
BEFORE UPDATE ON audit_events BEGIN SELECT RAISE(ABORT, 'audit events are append-only'); END;
CREATE TRIGGER IF NOT EXISTS audit_events_no_delete
BEFORE DELETE ON audit_events BEGIN SELECT RAISE(ABORT, 'audit events are append-only'); END;
CREATE TABLE IF NOT EXISTS paper_accounts (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    name TEXT NOT NULL,
    currency TEXT NOT NULL,
    initial_cash REAL NOT NULL CHECK(initial_cash >= 0),
    created_at TEXT NOT NULL,
    UNIQUE(user_id, name)
);
CREATE TABLE IF NOT EXISTS paper_orders (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    account_id TEXT NOT NULL REFERENCES paper_accounts(id),
    client_order_id TEXT NOT NULL,
    symbol TEXT NOT NULL,
    side TEXT NOT NULL CHECK(side IN ('buy','sell')),
    quantity REAL NOT NULL CHECK(quantity > 0),
    reference_price REAL NOT NULL CHECK(reference_price > 0),
    executed_price REAL NOT NULL CHECK(executed_price > 0),
    fee REAL NOT NULL CHECK(fee >= 0),
    status TEXT NOT NULL CHECK(status IN ('FILLED')),
    created_at TEXT NOT NULL,
    UNIQUE(user_id, client_order_id)
);
CREATE INDEX IF NOT EXISTS idx_paper_orders_account ON paper_orders(user_id, account_id, created_at);
"""


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class Database:
    """Connection-per-operation SQLite store; WAL and foreign keys are enabled."""

    def __init__(self, path: str | Path) -> None:
        self._memory = str(path) == ":memory:"
        self.path = (
            f"file:marketcouncil-{uuid.uuid4().hex}?mode=memory&cache=shared"
            if self._memory else str(Path(path).expanduser())
        )
        # Keep one shared-memory connection alive while per-operation connections
        # open and close around it. File-backed databases are recommended in use.
        self._keeper = sqlite3.connect(self.path, uri=True) if self._memory else None
        if not self._memory:
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    @contextmanager
    def connect(self):
        """Yield a configured connection and always commit/rollback/close it."""
        conn = sqlite3.connect(self.path, timeout=10, isolation_level="DEFERRED", uri=self._memory)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA busy_timeout = 10000")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def initialize(self) -> None:
        with self.connect() as conn:
            if not self._memory:
                conn.execute("PRAGMA journal_mode = WAL")
            conn.executescript(SCHEMA)


class AuditStore:
    def __init__(self, database: Database) -> None:
        self.database = database

    @staticmethod
    def record_in_connection(
        conn: sqlite3.Connection, *, user_id: str, action: str, entity_type: str,
        entity_id: str, metadata: dict[str, Any] | None = None,
    ) -> int:
        """Insert an audit event in the caller's transaction for atomicity."""
        values = (user_id, action, entity_type, entity_id)
        if not all(isinstance(value, str) and value.strip() for value in values):
            raise ValueError("audit identity and event fields must be non-empty strings")
        if len(action) > 100 or len(entity_type) > 100 or len(entity_id) > 200:
            raise ValueError("audit action/type/id exceeds its supported length")
        payload = {} if metadata is None else metadata
        if not isinstance(payload, dict):
            raise ValueError("audit metadata must be an object")
        try:
            metadata_json = json.dumps(payload, allow_nan=False, separators=(",", ":"))
        except (TypeError, ValueError, RecursionError) as exc:
            raise ValueError("audit metadata must be finite, JSON-serializable data") from exc
        if len(metadata_json.encode("utf-8")) > 20_000:
            raise ValueError("audit metadata exceeds 20 KB")
        cursor = conn.execute(
            "INSERT INTO audit_events(user_id,action,entity_type,entity_id,metadata_json,created_at) VALUES(?,?,?,?,?,?)",
            (user_id, action, entity_type, entity_id, metadata_json, utc_now()),
        )
        return int(cursor.lastrowid)

    def record(
        self, *, user_id: str, action: str, entity_type: str,
        entity_id: str, metadata: dict[str, Any] | None = None,
    ) -> int:
        with self.database.connect() as conn:
            return self.record_in_connection(
                conn, user_id=user_id, action=action, entity_type=entity_type,
                entity_id=entity_id, metadata=metadata,
            )

    def list_for_user(self, user_id: str, limit: int = 100) -> list[dict[str, Any]]:
        if not 1 <= limit <= 500:
            raise ValueError("limit must be between 1 and 500")
        with self.database.connect() as conn:
            rows = conn.execute(
                "SELECT id,action,entity_type,entity_id,metadata_json,created_at FROM audit_events WHERE user_id=? ORDER BY id DESC LIMIT ?",
                (user_id, limit),
            ).fetchall()
        return [{**dict(row), "metadata": json.loads(row["metadata_json"])} | {"metadata_json": None} for row in rows]

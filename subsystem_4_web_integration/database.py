"""Database - the SQLite connection and table definitions.

Data storage of the whole project (PPT: "SQLite tables may include waste items,
recycling rules, scan history ..."):

    users         login accounts (passwords are stored hashed, never as text)
    rules         recycling rules (Subsystem 3 data, edited by admins)
    scans         every analysed photo: label, confidence, bin, source, city, time
    usage_events  LLM usage per user (for the token statistics)
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from werkzeug.security import generate_password_hash


def utc_now() -> str:
    """Current time as an ISO-8601 UTC string, e.g. ``2026-11-10T14:03:21+00:00``."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class ClosingConnection(sqlite3.Connection):
    """``with db.connect() as c:`` should commit AND close the connection.

    (Plain sqlite3 only commits, which would leak open connections.)
    """

    def __exit__(self, exc_type, exc_value, traceback):
        result = super().__exit__(exc_type, exc_value, traceback)
        self.close()
        return result


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'municipality', 'admin')),
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS rules (
    label TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    bin TEXT NOT NULL,
    bin_de TEXT NOT NULL,
    color TEXT NOT NULL,
    hex TEXT NOT NULL,
    theme TEXT NOT NULL,
    symbol TEXT NOT NULL,
    note TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    image_path TEXT NOT NULL,
    model_label TEXT,
    model_confidence REAL,
    predicted_bin TEXT,
    prediction_source TEXT NOT NULL DEFAULT 'local',
    llm_used INTEGER NOT NULL DEFAULT 0,
    llm_tokens INTEGER NOT NULL DEFAULT 0,
    city TEXT NOT NULL DEFAULT 'Dortmund',
    created_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS usage_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    event_type TEXT NOT NULL,
    token_count INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
);
"""


class Database:
    """Opens connections and creates / seeds the tables."""

    def __init__(self, path: Path | str):
        self._path = Path(path)

    @property
    def path(self) -> Path:
        return self._path

    def connect(self) -> sqlite3.Connection:
        """New connection with dict-like rows and foreign keys switched on.

        A new connection per operation keeps the code thread-safe (Flask runs
        requests in several threads).
        """
        connection = sqlite3.connect(self._path, factory=ClosingConnection)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self, admin_username: str, admin_password: str, seed_rules: list[dict]) -> None:
        """Create tables, add missing columns, insert default rules and the admin user.

        Safe to call on every start: ``IF NOT EXISTS`` / ``INSERT OR IGNORE``
        never overwrite existing data.

        DEBUG: the database file lives in ``<data_dir>/sortly.sqlite3``; open
        it with any SQLite browser to inspect the tables.
        """
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript(SCHEMA)
            # Older databases did not have the 'city' column yet.
            scan_columns = {row["name"] for row in db.execute("PRAGMA table_info(scans)").fetchall()}
            if "city" not in scan_columns:
                db.execute("ALTER TABLE scans ADD COLUMN city TEXT NOT NULL DEFAULT 'Dortmund'")
            db.execute("UPDATE scans SET city='Dortmund' WHERE city IS NULL OR TRIM(city)=''")
            for rule in seed_rules:
                db.execute(
                    """INSERT OR IGNORE INTO rules
                    (label, category, bin, bin_de, color, hex, theme, symbol, note, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (rule["label"], rule["category"], rule["bin"], rule["bin_de"], rule["color"],
                     rule["hex"], rule["theme"], rule["symbol"], rule["note"], utc_now()))
            if db.execute("SELECT id FROM users WHERE username = ?", (admin_username,)).fetchone() is None:
                db.execute(
                    "INSERT INTO users(username, password_hash, role, created_at) VALUES (?, ?, 'admin', ?)",
                    (admin_username, generate_password_hash(admin_password), utc_now()))

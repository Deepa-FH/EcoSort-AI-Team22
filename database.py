"""SQLite persistence for the local Sortly waste assistant."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from werkzeug.security import check_password_hash, generate_password_hash


DEFAULT_RULES = {
    "Biomuell": {
        "category": "Organic waste", "bin": "Brown organic bin", "bin_de": "Biotonne",
        "color": "Brown", "hex": "#8B5E3C", "theme": "organic", "symbol": "leaf",
        "note": "Food scraps and accepted garden waste belong here. Check local rules for cooked food and compostable liners.",
    },
    "Glass": {
        "category": "Glass", "bin": "Deposit return or glass container", "bin_de": "Pfandautomat / Altglascontainer",
        "color": "Green / white / brown", "hex": "#4F8A67", "theme": "glass", "symbol": "bottle",
        "note": "Return deposit bottles first. Put non-deposit container glass into the matching white, green or brown container.",
    },
    "Metal": {
        "category": "Metal", "bin": "Yellow bin or recycling centre", "bin_de": "Gelbe Tonne / Wertstoffhof",
        "color": "Yellow", "hex": "#F4C542", "theme": "metal", "symbol": "can",
        "note": "Metal packaging usually belongs in the yellow bin. Other metal objects normally go to a recycling centre.",
    },
    "Papier": {
        "category": "Paper & cardboard", "bin": "Blue paper bin", "bin_de": "Papiertonne",
        "color": "Blue", "hex": "#3178C6", "theme": "paper", "symbol": "paper",
        "note": "Use for clean paper and flattened cardboard. Heavily soiled or coated paper may need residual waste.",
    },
    "Plastic": {
        "category": "Plastic", "bin": "Deposit return or yellow bin", "bin_de": "Pfandautomat / Gelbe Tonne",
        "color": "Yellow", "hex": "#F4C542", "theme": "plastic", "symbol": "bottle",
        "note": "Return bottles carrying a deposit symbol. Empty plastic packaging without a deposit usually goes in the yellow bin.",
    },
    "Sondermuell": {
        "category": "Special waste", "bin": "Special collection point", "bin_de": "Schadstoffmobil / Sammelstelle",
        "color": "Red", "hex": "#D94B4B", "theme": "special", "symbol": "battery",
        "note": "Batteries, chemicals and hazardous items must go to a designated collection point, never a household bin.",
    },
    "Textile_Trash": {
        "category": "Textiles", "bin": "Reuse or textile collection", "bin_de": "Altkleidercontainer / Spende",
        "color": "Orange", "hex": "#D9822B", "theme": "textile", "symbol": "shirt",
        "note": "Donate clean, wearable textiles or use a textile collection point. Wet or contaminated textiles follow local rules.",
    },
}


class ClosingConnection(sqlite3.Connection):
    """Make ``with database.connect()`` close the connection as well as commit."""

    def __exit__(self, exc_type, exc_value, traceback):
        result = super().__exit__(exc_type, exc_value, traceback)
        self.close()
        return result


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Database:
    def __init__(self, path: Path):
        self.path = path

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, factory=ClosingConnection)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def init(self, admin_username: str, admin_password: str) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript(
                """
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
            )
            scan_columns = {row["name"] for row in db.execute("PRAGMA table_info(scans)").fetchall()}
            if "city" not in scan_columns:
                db.execute("ALTER TABLE scans ADD COLUMN city TEXT NOT NULL DEFAULT 'Dortmund'")
            db.execute("UPDATE scans SET city='Dortmund' WHERE city IS NULL OR TRIM(city)=''")
            for label, rule in DEFAULT_RULES.items():
                db.execute(
                    """INSERT OR IGNORE INTO rules
                    (label, category, bin, bin_de, color, hex, theme, symbol, note, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (label, rule["category"], rule["bin"], rule["bin_de"], rule["color"],
                     rule["hex"], rule["theme"], rule["symbol"], rule["note"], utc_now()),
                )
            existing = db.execute("SELECT id FROM users WHERE username = ?", (admin_username,)).fetchone()
            if existing is None:
                db.execute(
                    "INSERT INTO users(username, password_hash, role, created_at) VALUES (?, ?, 'admin', ?)",
                    (admin_username, generate_password_hash(admin_password), utc_now()),
                )

    def authenticate(self, username: str, password: str) -> sqlite3.Row | None:
        with self.connect() as db:
            user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            if user and check_password_hash(user["password_hash"], password):
                return user
        return None

    def create_user(self, username: str, password: str, role: str) -> None:
        with self.connect() as db:
            db.execute(
                "INSERT INTO users(username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
                (username, generate_password_hash(password), role, utc_now()),
            )

    def rules(self) -> dict[str, dict[str, Any]]:
        with self.connect() as db:
            rows = db.execute("SELECT * FROM rules ORDER BY label").fetchall()
        return {row["label"]: dict(row) for row in rows}

    def update_rule(self, label: str, values: dict[str, str]) -> None:
        with self.connect() as db:
            db.execute(
                """UPDATE rules SET category=?, bin=?, bin_de=?, color=?, hex=?, theme=?, symbol=?, note=?, updated_at=?
                WHERE label=?""",
                (values["category"], values["bin"], values["bin_de"], values["color"], values["hex"],
                 values["theme"], values["symbol"], values["note"], utc_now(), label),
            )

    def add_scan(self, user_id: int | None, image_path: str, label: str | None, confidence: float | None,
                 predicted_bin: str | None, source: str = "local", llm_used: int = 0,
                 llm_tokens: int = 0, city: str = "Dortmund") -> int:
        with self.connect() as db:
            cursor = db.execute(
                """INSERT INTO scans(user_id, image_path, model_label, model_confidence, predicted_bin,
                prediction_source, llm_used, llm_tokens, city, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, image_path, label, confidence, predicted_bin, source, llm_used, llm_tokens,
                 city.strip() or "Dortmund", utc_now()),
            )
            return int(cursor.lastrowid)

    def update_scan_review(self, scan_id: int, source: str, tokens: int, predicted_bin: str | None) -> None:
        with self.connect() as db:
            db.execute(
                "UPDATE scans SET prediction_source=?, llm_used=1, llm_tokens=?, predicted_bin=? WHERE id=?",
                (source, tokens, predicted_bin, scan_id),
            )

    def add_usage(self, user_id: int | None, event_type: str, tokens: int) -> None:
        with self.connect() as db:
            db.execute(
                "INSERT INTO usage_events(user_id, event_type, token_count, created_at) VALUES (?, ?, ?, ?)",
                (user_id, event_type, tokens, utc_now()),
            )

    def history(self, limit: int = 100) -> list[dict[str, Any]]:
        with self.connect() as db:
            rows = db.execute(
                """SELECT scans.*, users.username FROM scans LEFT JOIN users ON users.id = scans.user_id
                ORDER BY scans.id DESC LIMIT ?""", (limit,)
            ).fetchall()
        return [dict(row) for row in rows]

    def stats(self, filters: dict[str, list[str]] | None = None) -> dict[str, Any]:
        filters = filters or {}
        has_filters = any(filters.values())
        with self.connect() as db:
            where = ["1=1"]
            params: list[str | float] = []

            labels = filters.get("labels", [])
            if labels:
                where.append("COALESCE(s.predicted_bin, 'Unknown') IN (" + ",".join("?" for _ in labels) + ")")
                params.extend(labels)
            categories = filters.get("categories", [])
            if categories:
                where.append("COALESCE(r.category, 'Unknown') IN (" + ",".join("?" for _ in categories) + ")")
                params.extend(categories)
            cities = filters.get("cities", [])
            if cities:
                where.append("s.city IN (" + ",".join("?" for _ in cities) + ")")
                params.extend(cities)
            months = filters.get("months", [])
            if months:
                where.append("substr(s.created_at, 1, 7) IN (" + ",".join("?" for _ in months) + ")")
                params.extend(months)
            confidence_bands = filters.get("confidence", [])
            if confidence_bands:
                band_clauses = []
                for band in confidence_bands:
                    if band == "high":
                        band_clauses.append("s.model_confidence >= 0.80")
                    elif band == "medium":
                        band_clauses.append("s.model_confidence >= 0.50 AND s.model_confidence < 0.80")
                    elif band == "low":
                        band_clauses.append("s.model_confidence < 0.50 OR s.model_confidence IS NULL")
                if band_clauses:
                    where.append("(" + " OR ".join(band_clauses) + ")")
            condition = " AND ".join(where)
            by_bin = db.execute(
                f"SELECT COALESCE(s.predicted_bin, 'Unknown') AS label, COUNT(*) AS count FROM scans s "
                f"LEFT JOIN rules r ON r.label = s.predicted_bin WHERE {condition} "
                "GROUP BY COALESCE(s.predicted_bin, 'Unknown') ORDER BY count DESC", params
            ).fetchall()
            by_source = db.execute(
                f"SELECT s.prediction_source AS label, COUNT(*) AS count FROM scans s "
                f"LEFT JOIN rules r ON r.label = s.predicted_bin WHERE {condition} GROUP BY s.prediction_source", params
            ).fetchall()
            totals = db.execute(
                f"SELECT COUNT(*) AS scans, COALESCE(SUM(s.llm_used),0) AS llm_calls, "
                f"COALESCE(SUM(s.llm_tokens),0) AS scan_tokens FROM scans s "
                f"LEFT JOIN rules r ON r.label = s.predicted_bin WHERE {condition}", params
            ).fetchone()
            usage = db.execute("SELECT COALESCE(SUM(token_count),0) AS tokens FROM usage_events").fetchone()
            categories = db.execute("SELECT DISTINCT category FROM rules ORDER BY category").fetchall()
            cities = db.execute("SELECT DISTINCT city FROM scans WHERE city IS NOT NULL AND TRIM(city) != '' ORDER BY city").fetchall()
            months = db.execute("SELECT DISTINCT substr(created_at, 1, 7) AS month FROM scans ORDER BY month DESC").fetchall()
        return {
            "by_bin": [dict(row) for row in by_bin],
            "by_source": [dict(row) for row in by_source],
            "totals": {"scans": totals["scans"], "llm_calls": totals["llm_calls"],
                       "tokens": totals["scan_tokens"] + (0 if has_filters else usage["tokens"])},
            "filters": {
                "categories": [row["category"] for row in categories],
                "cities": [row["city"] for row in cities] or ["Dortmund"],
                "months": [row["month"] for row in months],
                "confidence": ["high", "medium", "low"],
            },
        }

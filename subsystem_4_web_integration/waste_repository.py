"""WasteRepository - reads and writes scans, rules and usage in SQLite.

OOP idea: REPOSITORY PATTERN. All SQL lives here; the rest of the program
never writes SQL, so changing the database (e.g. to MySQL, see Home Task 3)
only affects this file.

It also satisfies the ``RuleStore`` protocol of Subsystem 3
(``fetch_rules`` / ``save_rule``), so the rule engine can use it directly.
"""

from __future__ import annotations

from typing import Any

from .database import Database, utc_now


class WasteRepository:
    """Data access for rules, scans and LLM usage."""

    def __init__(self, database: Database):
        self._db = database

    # ---- rules (RuleStore protocol) -------------------------------------
    def fetch_rules(self) -> dict[str, dict[str, Any]]:
        """All rules as ``{label: row-dict}``, ordered by label."""
        with self._db.connect() as db:
            rows = db.execute("SELECT * FROM rules ORDER BY label").fetchall()
        return {row["label"]: dict(row) for row in rows}

    def save_rule(self, label: str, values: dict[str, str]) -> None:
        """Overwrite the editable fields of one rule."""
        with self._db.connect() as db:
            db.execute(
                """UPDATE rules SET category=?, bin=?, bin_de=?, color=?, hex=?, theme=?, symbol=?, note=?,
                updated_at=? WHERE label=?""",
                (values["category"], values["bin"], values["bin_de"], values["color"], values["hex"],
                 values["theme"], values["symbol"], values["note"], utc_now(), label))

    # ---- scans -----------------------------------------------------------
    def add_scan(self, user_id: int | None, image_path: str, label: str | None, confidence: float | None,
                 predicted_bin: str | None, source: str = "local", llm_used: int = 0,
                 llm_tokens: int = 0, city: str = "Dortmund") -> int:
        """Insert one scan and return its new id."""
        with self._db.connect() as db:
            cursor = db.execute(
                """INSERT INTO scans(user_id, image_path, model_label, model_confidence, predicted_bin,
                prediction_source, llm_used, llm_tokens, city, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, image_path, label, confidence, predicted_bin, source, llm_used, llm_tokens,
                 city.strip() or "Dortmund", utc_now()))
            return int(cursor.lastrowid)

    def update_scan_review(self, scan_id: int, source: str, tokens: int,
                           predicted_bin: str | None, llm_used: bool = True) -> None:
        """Store the result of the second-opinion review on an existing scan.

        ``predicted_bin`` is only replaced when the review found a matching rule.
        """
        with self._db.connect() as db:
            db.execute(
                """UPDATE scans SET prediction_source=?, llm_used=?, llm_tokens=?,
                predicted_bin=COALESCE(?, predicted_bin) WHERE id=?""",
                (source, 1 if llm_used else 0, tokens, predicted_bin, scan_id))

    def history(self, limit: int = 100) -> list[dict[str, Any]]:
        """Newest scans first, including the username of the scanner."""
        with self._db.connect() as db:
            rows = db.execute(
                """SELECT scans.*, users.username FROM scans LEFT JOIN users ON users.id = scans.user_id
                ORDER BY scans.id DESC LIMIT ?""", (limit,)).fetchall()
        return [dict(row) for row in rows]

    # ---- LLM usage -------------------------------------------------------
    def add_usage(self, user_id: int | None, event_type: str, tokens: int) -> None:
        """Record one LLM call (``review`` or ``chat``) with its token estimate."""
        with self._db.connect() as db:
            db.execute("INSERT INTO usage_events(user_id, event_type, token_count, created_at) VALUES (?, ?, ?, ?)",
                       (user_id, event_type, tokens, utc_now()))

    # ---- statistics (dashboard) -----------------------------------------
    def stats(self, filters: dict[str, list[str]] | None = None) -> dict[str, Any]:
        """Aggregate numbers for the dashboard, optionally filtered.

        ``filters`` keys: ``labels``, ``categories``, ``cities``, ``months``,
        ``confidence`` (``high`` / ``medium`` / ``low``).

        DEBUG: print ``condition`` and ``params`` to see the generated WHERE
        clause. Values are always passed as ``?`` parameters (no SQL injection).
        """
        filters = filters or {}
        has_filters = any(filters.values())
        with self._db.connect() as db:
            where = ["1=1"]
            params: list[str | float] = []

            labels = filters.get("labels", [])
            if labels:
                where.append("COALESCE(s.predicted_bin, 'Unknown') IN (" + ",".join("?" for _ in labels) + ")")
                params.extend(labels)
            wanted_categories = filters.get("categories", [])
            if wanted_categories:
                where.append("COALESCE(r.category, 'Unknown') IN (" + ",".join("?" for _ in wanted_categories) + ")")
                params.extend(wanted_categories)
            wanted_cities = filters.get("cities", [])
            if wanted_cities:
                where.append("s.city IN (" + ",".join("?" for _ in wanted_cities) + ")")
                params.extend(wanted_cities)
            wanted_months = filters.get("months", [])
            if wanted_months:
                where.append("substr(s.created_at, 1, 7) IN (" + ",".join("?" for _ in wanted_months) + ")")
                params.extend(wanted_months)
            bands = filters.get("confidence", [])
            if bands:
                clauses = []
                for band in bands:
                    if band == "high":
                        clauses.append("s.model_confidence >= 0.80")
                    elif band == "medium":
                        clauses.append("s.model_confidence >= 0.50 AND s.model_confidence < 0.80")
                    elif band == "low":
                        clauses.append("s.model_confidence < 0.50 OR s.model_confidence IS NULL")
                if clauses:
                    where.append("(" + " OR ".join(clauses) + ")")
            condition = " AND ".join(where)

            by_bin = db.execute(
                "SELECT COALESCE(s.predicted_bin, 'Unknown') AS label, COUNT(*) AS count FROM scans s "
                f"LEFT JOIN rules r ON r.label = s.predicted_bin WHERE {condition} "
                "GROUP BY COALESCE(s.predicted_bin, 'Unknown') ORDER BY count DESC", params).fetchall()
            by_source = db.execute(
                "SELECT s.prediction_source AS label, COUNT(*) AS count FROM scans s "
                f"LEFT JOIN rules r ON r.label = s.predicted_bin WHERE {condition} "
                "GROUP BY s.prediction_source", params).fetchall()
            totals = db.execute(
                "SELECT COUNT(*) AS scans, COALESCE(SUM(s.llm_used),0) AS llm_calls, "
                "COALESCE(SUM(s.llm_tokens),0) AS scan_tokens FROM scans s "
                f"LEFT JOIN rules r ON r.label = s.predicted_bin WHERE {condition}", params).fetchone()
            usage = db.execute("SELECT COALESCE(SUM(token_count),0) AS tokens FROM usage_events").fetchone()
            all_categories = db.execute("SELECT DISTINCT category FROM rules ORDER BY category").fetchall()
            all_cities = db.execute(
                "SELECT DISTINCT city FROM scans WHERE city IS NOT NULL AND TRIM(city) != '' ORDER BY city").fetchall()
            all_months = db.execute(
                "SELECT DISTINCT substr(created_at, 1, 7) AS month FROM scans ORDER BY month DESC").fetchall()
        return {
            "by_bin": [dict(row) for row in by_bin],
            "by_source": [dict(row) for row in by_source],
            "totals": {"scans": totals["scans"], "llm_calls": totals["llm_calls"],
                       "tokens": totals["scan_tokens"] + (0 if has_filters else usage["tokens"])},
            "filters": {
                "categories": [row["category"] for row in all_categories],
                "cities": [row["city"] for row in all_cities] or ["Dortmund"],
                "months": [row["month"] for row in all_months],
                "confidence": ["high", "medium", "low"],
            },
        }

"""Database access layer for waste scan records."""
from __future__ import annotations

from typing import Any

from database import MySQLDatabase


class ScanRepository:
    def __init__(self, database: MySQLDatabase) -> None:
        self._database = database

    def list_all(self) -> list[dict[str, Any]]:
        with self._database.connection() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM waste_scans ORDER BY id DESC")
            rows = cursor.fetchall()
            cursor.close()
        return rows

    def get(self, scan_id: int) -> dict[str, Any] | None:
        with self._database.connection() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM waste_scans WHERE id = %s", (scan_id,))
            row = cursor.fetchone()
            cursor.close()
        return row

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        sql = """INSERT INTO waste_scans
            (item_name, material_category, confidence, disposal_bin, city, notes)
            VALUES (%s, %s, %s, %s, %s, %s)"""
        values = (
            data["item_name"], data["material_category"], data["confidence"],
            data["disposal_bin"], data["city"], data.get("notes", ""),
        )
        with self._database.connection() as connection:
            cursor = connection.cursor()
            cursor.execute(sql, values)
            scan_id = int(cursor.lastrowid)
            cursor.close()
        return self.get(scan_id)

    def update(self, scan_id: int, data: dict[str, Any]) -> dict[str, Any] | None:
        sql = """UPDATE waste_scans SET item_name=%s, material_category=%s,
            confidence=%s, disposal_bin=%s, city=%s, notes=%s WHERE id=%s"""
        values = (
            data["item_name"], data["material_category"], data["confidence"],
            data["disposal_bin"], data["city"], data.get("notes", ""), scan_id,
        )
        with self._database.connection() as connection:
            cursor = connection.cursor()
            cursor.execute(sql, values)
            changed = cursor.rowcount
            cursor.close()
        return self.get(scan_id) if changed else None

    def delete(self, scan_id: int) -> bool:
        with self._database.connection() as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM waste_scans WHERE id = %s", (scan_id,))
            changed = cursor.rowcount
            cursor.close()
        return bool(changed)

    def statistics(self) -> dict[str, Any]:
        with self._database.connection() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT COUNT(*) AS total, ROUND(AVG(confidence), 3) AS average_confidence FROM waste_scans")
            summary = cursor.fetchone()
            cursor.execute("SELECT material_category AS category, COUNT(*) AS count FROM waste_scans GROUP BY material_category ORDER BY count DESC")
            categories = cursor.fetchall()
            cursor.close()
        return {"summary": summary, "by_category": categories}

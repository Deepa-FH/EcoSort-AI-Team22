"""EcoSort AI Home Task 3: Flask REST API with a MySQL access layer."""
from __future__ import annotations

import time

from flask import Flask, jsonify, render_template, request
from mysql.connector import Error as MySQLError

from config import Config
from database import MySQLDatabase
from repositories import ScanRepository
from services import ScanService, ValidationError


def create_app(service=None, database=None) -> Flask:
    app = Flask(__name__)
    if service is None:
        db_config = {
            "host": Config.MYSQL_HOST,
            "port": Config.MYSQL_PORT,
            "database": Config.MYSQL_DATABASE,
            "user": Config.MYSQL_USER,
            "password": Config.MYSQL_PASSWORD,
        }
        database = database or MySQLDatabase(db_config)
        service = ScanService(ScanRepository(database))
    app.extensions["scan_service"] = service
    app.extensions["mysql_database"] = database

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/health")
    def health():
        if app.extensions["mysql_database"] is not None:
            app.extensions["mysql_database"].ping()
        return jsonify(status="healthy", application="EcoSort AI Scan Database")

    @app.get("/api/scans")
    def list_scans():
        return jsonify(service.list_scans())

    @app.get("/api/scans/<int:scan_id>")
    def get_scan(scan_id: int):
        record = service.get_scan(scan_id)
        return (jsonify(record), 200) if record else (jsonify(error="Scan not found"), 404)

    @app.post("/api/scans")
    def create_scan():
        record = service.create_scan(request.get_json(silent=True) or {})
        return jsonify(record), 201

    @app.put("/api/scans/<int:scan_id>")
    def update_scan(scan_id: int):
        record = service.update_scan(scan_id, request.get_json(silent=True) or {})
        return (jsonify(record), 200) if record else (jsonify(error="Scan not found"), 404)

    @app.delete("/api/scans/<int:scan_id>")
    def delete_scan(scan_id: int):
        return ("", 204) if service.delete_scan(scan_id) else (jsonify(error="Scan not found"), 404)

    @app.get("/api/stats")
    def statistics():
        return jsonify(service.statistics())

    @app.errorhandler(ValidationError)
    def validation_error(error):
        return jsonify(error=str(error)), 400

    @app.errorhandler(MySQLError)
    def database_error(error):
        app.logger.exception("MySQL operation failed")
        return jsonify(error="Database operation failed", detail=str(error)), 503

    return app


def create_app_with_retry(attempts: int = 20, delay: float = 2.0) -> Flask:
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            application = create_app()
            application.extensions["mysql_database"].ping()
            return application
        except MySQLError as exc:
            last_error = exc
            print(f"Waiting for MySQL ({attempt}/{attempts}): {exc}")
            time.sleep(delay)
    raise RuntimeError(f"MySQL did not become ready: {last_error}")


if __name__ == "__main__":
    app = create_app_with_retry()
    app.run(host=Config.APP_HOST, port=Config.APP_PORT, debug=Config.DEBUG)

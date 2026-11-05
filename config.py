"""Portable environment-based application configuration."""
from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "ecosort")
    MYSQL_USER = os.getenv("MYSQL_USER", "ecosort_user")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "ecosort_password")
    APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT = int(os.getenv("APP_PORT", "5000"))
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"

"""UserRepository + AuthService - accounts, passwords and roles."""

from __future__ import annotations

import hmac
import sqlite3
from typing import Any

from werkzeug.security import check_password_hash, generate_password_hash

from .database import Database, utc_now
from .exceptions import AuthenticationError, UserExistsError, ValidationFailedError

VALID_ROLES = ("user", "municipality", "admin")


class UserRepository:
    """SQL for the ``users`` table."""

    def __init__(self, database: Database):
        self._db = database

    def find_by_username(self, username: str) -> sqlite3.Row | None:
        with self._db.connect() as db:
            return db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

    def create(self, username: str, password: str, role: str) -> None:
        """Insert a user. The password is hashed (salted PBKDF2/scrypt), never stored as text."""
        try:
            with self._db.connect() as db:
                db.execute("INSERT INTO users(username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
                           (username, generate_password_hash(password), role, utc_now()))
        except sqlite3.IntegrityError as error:      # UNIQUE(username) violated
            raise UserExistsError() from error


class AuthService:
    """Login and sign-up rules (business logic, no Flask code here)."""

    def __init__(self, users: UserRepository, signup_code: str):
        self._users = users
        self._signup_code = signup_code

    def login(self, username: str, password: str, role: str | None = None) -> dict[str, Any]:
        """Return ``{"id", "username", "role"}`` or raise ``AuthenticationError``.

        ``role`` is the "Sign in as" choice on the login form. If given, it must
        match the role stored for the account (a normal user cannot enter as admin).
        """
        row = self._users.find_by_username(username)
        if (row is None or not check_password_hash(row["password_hash"], password)
                or (role and row["role"] != role)):
            # One error for "no such user", "wrong password" and "wrong role" (leaks nothing).
            raise AuthenticationError("Incorrect username, password or role.")
        return {"id": row["id"], "username": row["username"], "role": row["role"]}

    def register(self, username: str, password: str, role: str, code: str) -> None:
        """Create an account after checking the invitation code and the inputs."""
        # compare_digest compares in constant time (protects against timing attacks).
        if not hmac.compare_digest(code.encode(), self._signup_code.encode()):
            raise ValidationFailedError("The invitation code is incorrect.")
        if len(username) < 3 or len(password) < 6:
            raise ValidationFailedError(
                "Use a username with at least 3 characters and a password with at least 6 characters.")
        if role not in VALID_ROLES:
            raise ValidationFailedError("Choose a valid account type.")
        self._users.create(username, password, role)

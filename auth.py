from __future__ import annotations

import hashlib
import hmac
import os
from sqlite3 import IntegrityError

from db import get_connection


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return f"{salt.hex()}:{digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        salt_hex, digest_hex = password_hash.split(":", 1)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
    except ValueError:
        return False

    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return hmac.compare_digest(actual, expected)


def register_user(username: str, email: str, password: str, db_path=None) -> tuple[bool, str]:
    username = username.strip()
    email = email.strip().lower()

    if len(username) < 3:
        return False, "Der Benutzername muss mindestens 3 Zeichen lang sein."
    if "@" not in email:
        return False, "Bitte gib eine gueltige E-Mail-Adresse ein."
    if len(password) < 6:
        return False, "Das Passwort muss mindestens 6 Zeichen lang sein."

    try:
        with get_connection(db_path) as conn:
            conn.execute(
                """
                INSERT INTO users (username, email, password_hash, display_name)
                VALUES (?, ?, ?, ?)
                """,
                (username, email, hash_password(password), username),
            )
    except IntegrityError:
        return False, "Benutzername oder E-Mail ist bereits vergeben."

    return True, "Registrierung erfolgreich. Du kannst dich jetzt einloggen."


def authenticate_user(identifier: str, password: str, db_path=None) -> dict | None:
    identifier = identifier.strip().lower()
    with get_connection(db_path) as conn:
        user = conn.execute(
            """
            SELECT * FROM users
            WHERE lower(username) = ? OR lower(email) = ?
            """,
            (identifier, identifier),
        ).fetchone()

    if user and verify_password(password, user["password_hash"]):
        return dict(user)
    return None


def get_user(user_id: int, db_path=None) -> dict | None:
    with get_connection(db_path) as conn:
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return dict(user) if user else None

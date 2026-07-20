"""Silver — authentication and account management."""
import hashlib
import os
import re
import secrets
import sqlite3
import time
from typing import Optional

from . import db

USERNAME_RE = re.compile(r"^[a-zA-Z0-9_\.]{3,30}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 200_000).hex()


def register(conn: sqlite3.Connection, username: str, email: str, password: str,
             display_name: str) -> tuple[Optional[int], str]:
    """Create a user. Returns (user_id, "") or (None, error_key)."""
    username = username.strip().lower()
    email = email.strip().lower()
    if not USERNAME_RE.match(username):
        return None, "err_username"
    if not EMAIL_RE.match(email):
        return None, "err_email"
    if len(password) < 8:
        return None, "err_password_short"
    if not display_name.strip():
        return None, "err_name"
    salt = secrets.token_hex(16)
    try:
        cur = conn.execute(
            "INSERT INTO users (username, email, password_hash, salt, created_at) VALUES (?,?,?,?,?)",
            (username, email, hash_password(password, salt), salt, time.time()),
        )
    except sqlite3.IntegrityError:
        return None, "err_taken"
    uid = cur.lastrowid
    conn.execute("INSERT INTO profiles (user_id, display_name) VALUES (?,?)", (uid, display_name.strip()))
    conn.execute("INSERT INTO user_settings (user_id) VALUES (?)", (uid,))
    conn.commit()
    return uid, ""


def login(conn: sqlite3.Connection, identifier: str, password: str) -> tuple[Optional[sqlite3.Row], str]:
    """Login by username or email. Returns (user_row, "") or (None, error_key)."""
    identifier = identifier.strip().lower()
    row = conn.execute(
        "SELECT * FROM users WHERE username=? OR email=?", (identifier, identifier)
    ).fetchone()
    if row is None:
        return None, "err_login"
    if hash_password(password, row["salt"]) != row["password_hash"]:
        return None, "err_login"
    if row["status"] == "suspended":
        return None, "err_suspended"
    if row["status"] == "closed":
        return None, "err_closed"
    conn.execute("UPDATE users SET last_login_at=? WHERE id=?", (time.time(), row["id"]))
    conn.commit()
    return row, ""


def ensure_admin(conn: sqlite3.Connection) -> None:
    """Bootstrap the admin account from environment variables on first run."""
    existing = conn.execute("SELECT 1 FROM users WHERE role='admin' LIMIT 1").fetchone()
    if existing:
        return
    username = os.environ.get("SILVER_ADMIN_USERNAME", "admin")
    email = os.environ.get("SILVER_ADMIN_EMAIL", "admin@silver.local")
    password = os.environ.get("SILVER_ADMIN_PASSWORD", "ChangeMe_123")
    uid, err = register(conn, username, email, password, "Silver Admin")
    if uid is None:
        return
    conn.execute("UPDATE users SET role='admin' WHERE id=?", (uid,))
    conn.execute(
        "INSERT INTO audit_logs (actor_id, action, detail, created_at) VALUES (?,?,?,?)",
        (uid, "bootstrap_admin", f"admin account '{username}' created", time.time()),
    )
    conn.commit()
    _ = err


def change_password(conn: sqlite3.Connection, user_id: int, old: str, new: str) -> str:
    row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    if hash_password(old, row["salt"]) != row["password_hash"]:
        return "err_login"
    if len(new) < 8:
        return "err_password_short"
    salt = secrets.token_hex(16)
    conn.execute(
        "UPDATE users SET password_hash=?, salt=? WHERE id=?",
        (hash_password(new, salt), salt, user_id),
    )
    conn.commit()
    return ""


def delete_account(conn: sqlite3.Connection, user_id: int) -> None:
    conn.execute("UPDATE users SET status='closed' WHERE id=?", (user_id,))
    conn.commit()


def get_user(conn: sqlite3.Connection, user_id: int):
    return conn.execute(
        "SELECT u.*, p.display_name, p.bio, p.city, p.link, p.avatar_path, p.cover_path, p.is_private "
        "FROM users u JOIN profiles p ON p.user_id=u.id WHERE u.id=?",
        (user_id,),
    ).fetchone()


_ = db  # imported for path side effects

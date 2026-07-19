"""قاعدة بيانات SQLite بسيطة لتتبع المنتجات والطلبات والأرباح."""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "income_factory.db"


def _conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                kind TEXT NOT NULL,
                niche TEXT NOT NULL,
                language TEXT,
                notes TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                platform TEXT NOT NULL,
                item TEXT NOT NULL,
                amount_usd REAL NOT NULL,
                notes TEXT DEFAULT ''
            );
            """
        )


def add_product(kind: str, niche: str, language: str, notes: str = ""):
    with _conn() as conn:
        conn.execute(
            "INSERT INTO products (created_at, kind, niche, language, notes) VALUES (?, ?, ?, ?, ?)",
            (datetime.now().strftime("%Y-%m-%d %H:%M"), kind, niche, language, notes),
        )


def list_products():
    with _conn() as conn:
        rows = conn.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
    return [dict(r) for r in rows]


def add_order(platform: str, item: str, amount_usd: float, notes: str = ""):
    with _conn() as conn:
        conn.execute(
            "INSERT INTO orders (created_at, platform, item, amount_usd, notes) VALUES (?, ?, ?, ?, ?)",
            (datetime.now().strftime("%Y-%m-%d %H:%M"), platform, item, amount_usd, notes),
        )


def list_orders():
    with _conn() as conn:
        rows = conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
    return [dict(r) for r in rows]


def total_revenue() -> float:
    with _conn() as conn:
        row = conn.execute("SELECT COALESCE(SUM(amount_usd), 0) AS total FROM orders").fetchone()
    return float(row["total"])

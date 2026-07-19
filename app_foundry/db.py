"""سجل مشاريع الورشة — SQLite."""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "app_foundry.db"


def _conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                title TEXT NOT NULL,
                kind TEXT NOT NULL,
                client TEXT DEFAULT '',
                price_usd REAL DEFAULT 0,
                status TEXT DEFAULT 'قيد العمل',
                code TEXT DEFAULT ''
            )
            """
        )


def save_project(title: str, kind: str, code: str, client: str = "",
                 price_usd: float = 0.0, status: str = "قيد العمل") -> int:
    with _conn() as conn:
        cur = conn.execute(
            "INSERT INTO projects (created_at, title, kind, client, price_usd, status, code) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (datetime.now().strftime("%Y-%m-%d %H:%M"), title, kind, client, price_usd, status, code),
        )
        return cur.lastrowid


def update_code(project_id: int, code: str):
    with _conn() as conn:
        conn.execute("UPDATE projects SET code = ? WHERE id = ?", (code, project_id))


def update_status(project_id: int, status: str, price_usd: float = None):
    with _conn() as conn:
        if price_usd is not None:
            conn.execute("UPDATE projects SET status = ?, price_usd = ? WHERE id = ?",
                         (status, price_usd, project_id))
        else:
            conn.execute("UPDATE projects SET status = ? WHERE id = ?", (status, project_id))


def list_projects():
    with _conn() as conn:
        rows = conn.execute(
            "SELECT id, created_at, title, kind, client, price_usd, status FROM projects ORDER BY id DESC"
        ).fetchall()
    return [dict(r) for r in rows]


def get_code(project_id: int) -> str:
    with _conn() as conn:
        row = conn.execute("SELECT code FROM projects WHERE id = ?", (project_id,)).fetchone()
    return row["code"] if row else ""


def total_earnings() -> float:
    with _conn() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(price_usd), 0) AS t FROM projects WHERE status = 'مُسلَّم ومدفوع'"
        ).fetchone()
    return float(row["t"])

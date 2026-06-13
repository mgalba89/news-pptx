import sqlite3
from contextlib import closing

DB_PATH = "news.db"


def _conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    with closing(_conn()) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                source TEXT,
                summary TEXT NOT NULL,
                used INTEGER DEFAULT 0,
                added_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def add_item(type_, source, summary):
    with closing(_conn()) as conn:
        conn.execute(
            "INSERT INTO items (type, source, summary) VALUES (?, ?, ?)",
            (type_, source, summary)
        )
        conn.commit()


def get_pending_items():
    with closing(_conn()) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM items WHERE used = 0 ORDER BY added_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def mark_as_used(ids):
    if not ids:
        return
    with closing(_conn()) as conn:
        placeholders = ",".join("?" * len(ids))
        conn.execute(f"UPDATE items SET used = 1 WHERE id IN ({placeholders})", ids)
        conn.commit()


def get_all_items():
    with closing(_conn()) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM items ORDER BY added_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def delete_item(id_):
    with closing(_conn()) as conn:
        conn.execute("DELETE FROM items WHERE id = ?", (id_,))
        conn.commit()


def get_pending_items_in_range(date_from, date_to):
    with closing(_conn()) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM items WHERE used = 0 AND date(added_at) BETWEEN ? AND ? ORDER BY added_at DESC",
            (date_from, date_to)
        ).fetchall()
        return [dict(r) for r in rows]

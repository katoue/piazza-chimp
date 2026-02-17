# Piazza-Chimp Database Layer
# SQLite persistence for tracking answered posts

import sqlite3
from datetime import datetime


def init_db(db_path: str) -> sqlite3.Connection:
    """Initialize database and create answered_posts table if not exists."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS answered_posts (
            post_id TEXT PRIMARY KEY,
            post_nr INTEGER,
            answered_at TEXT
        )
    """)
    conn.commit()
    return conn


def already_answered(conn: sqlite3.Connection, post_id: str) -> bool:
    """Check if a post has already been answered by the bot."""
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM answered_posts WHERE post_id = ?", (post_id,))
    return cursor.fetchone() is not None


def mark_answered(conn: sqlite3.Connection, post_id: str, post_nr: int) -> None:
    """Mark a post as answered, recording the timestamp."""
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    cursor.execute(
        "INSERT OR IGNORE INTO answered_posts (post_id, post_nr, answered_at) VALUES (?, ?, ?)",
        (post_id, post_nr, now)
    )
    conn.commit()

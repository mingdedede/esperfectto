import sqlite3
import os
import json
from datetime import datetime, date
from typing import Optional


DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "esperfectto.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            bean_name TEXT NOT NULL,
            brand TEXT NOT NULL,
            roast_level TEXT NOT NULL,
            origin TEXT NOT NULL,
            process_method TEXT NOT NULL,

            -- Recommended settings
            rec_grind INTEGER NOT NULL,
            rec_dose_grams REAL NOT NULL,
            rec_dose_dial INTEGER NOT NULL,
            rec_temp INTEGER NOT NULL,
            rec_explanation TEXT NOT NULL,

            -- User feedback (filled after pulling)
            rating_sweetness INTEGER,
            rating_acidity INTEGER,
            rating_bitterness INTEGER,
            rating_body INTEGER,
            rating_overall INTEGER,
            feedback_notes TEXT,

            -- Was the recommendation adjusted by user before pulling?
            actual_grind INTEGER,
            actual_dose_grams REAL,
            actual_dose_dial INTEGER,
            actual_temp INTEGER
        );

        CREATE TABLE IF NOT EXISTS user_stats (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            total_xp INTEGER NOT NULL DEFAULT 0,
            total_shots INTEGER NOT NULL DEFAULT 0,
            current_streak INTEGER NOT NULL DEFAULT 0,
            best_streak INTEGER NOT NULL DEFAULT 0,
            last_session_date TEXT
        );

        -- Initialize stats row if not exists
        INSERT OR IGNORE INTO user_stats (id, total_xp, total_shots, current_streak, best_streak)
        VALUES (1, 0, 0, 0, 0);
    """)

    conn.commit()
    conn.close()


def save_session(
    bean_name: str,
    brand: str,
    roast_level: str,
    origin: str,
    process_method: str,
    rec_grind: int,
    rec_dose_grams: float,
    rec_dose_dial: int,
    rec_temp: int,
    rec_explanation: str,
) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO sessions
        (bean_name, brand, roast_level, origin, process_method,
         rec_grind, rec_dose_grams, rec_dose_dial, rec_temp, rec_explanation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (bean_name, brand, roast_level, origin, process_method,
         rec_grind, rec_dose_grams, rec_dose_dial, rec_temp, rec_explanation),
    )
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id


def save_feedback(
    session_id: int,
    sweetness: int,
    acidity: int,
    bitterness: int,
    body: int,
    overall: int,
    notes: str = "",
    actual_grind: Optional[int] = None,
    actual_dose_grams: Optional[float] = None,
    actual_dose_dial: Optional[int] = None,
    actual_temp: Optional[int] = None,
):
    conn = get_connection()
    conn.execute(
        """UPDATE sessions SET
            rating_sweetness=?, rating_acidity=?, rating_bitterness=?,
            rating_body=?, rating_overall=?, feedback_notes=?,
            actual_grind=?, actual_dose_grams=?, actual_dose_dial=?, actual_temp=?
        WHERE id=?""",
        (sweetness, acidity, bitterness, body, overall, notes,
         actual_grind, actual_dose_grams, actual_dose_dial, actual_temp,
         session_id),
    )
    conn.commit()
    conn.close()


def get_similar_sessions(roast_level: str, origin: str, process_method: str, limit: int = 20):
    conn = get_connection()
    rows = conn.execute(
        """SELECT * FROM sessions
        WHERE rating_overall IS NOT NULL
        AND roast_level=? AND origin=? AND process_method=?
        ORDER BY created_at DESC LIMIT ?""",
        (roast_level, origin, process_method, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_sessions(limit: int = 50):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM sessions ORDER BY created_at DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_favorite_bean() -> Optional[dict]:
    """Return the bean (name + brand) with the most sessions pulled."""
    conn = get_connection()
    row = conn.execute(
        """SELECT bean_name, brand, COUNT(*) as pull_count,
           ROUND(AVG(rating_overall), 1) as avg_rating
        FROM sessions
        GROUP BY bean_name, brand
        ORDER BY pull_count DESC, avg_rating DESC
        LIMIT 1""",
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_stats() -> dict:
    conn = get_connection()
    row = conn.execute("SELECT * FROM user_stats WHERE id=1").fetchone()
    conn.close()
    return dict(row) if row else {"total_xp": 0, "total_shots": 0, "current_streak": 0, "best_streak": 0}


def update_stats_after_session(xp_earned: int):
    conn = get_connection()
    stats = dict(conn.execute("SELECT * FROM user_stats WHERE id=1").fetchone())

    today = date.today().isoformat()
    last_date = stats["last_session_date"]

    new_streak = stats["current_streak"]
    if last_date is None:
        new_streak = 1
    elif last_date == today:
        pass  # Already pulled today, streak unchanged
    elif last_date == (date.today().replace(day=date.today().day - 1)).isoformat() if date.today().day > 1 else None:
        new_streak += 1
    else:
        # Check if yesterday properly
        from datetime import timedelta
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        if last_date == yesterday:
            new_streak += 1
        else:
            new_streak = 1

    best_streak = max(stats["best_streak"], new_streak)

    conn.execute(
        """UPDATE user_stats SET
            total_xp = total_xp + ?,
            total_shots = total_shots + 1,
            current_streak = ?,
            best_streak = ?,
            last_session_date = ?
        WHERE id=1""",
        (xp_earned, new_streak, best_streak, today),
    )
    conn.commit()
    conn.close()

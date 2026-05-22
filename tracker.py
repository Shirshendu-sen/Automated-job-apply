# tracker.py
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "logs", "applications.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title   TEXT,
            company     TEXT,
            platform    TEXT,
            status      TEXT,       -- 'applied', 'skipped', 'failed'
            reason      TEXT,       -- why it was skipped or failed
            job_url     TEXT,       -- optional; may be empty when URL is unavailable
            applied_at  TEXT
        )
    """)
    # Separate index only on non-empty URLs — avoids the blank-string UNIQUE clash
    # that would silently swallow every log entry after the first URL-less row.
    conn.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_job_url
        ON applications (job_url)
        WHERE job_url IS NOT NULL AND job_url != ''
    """)
    conn.commit()
    return conn

def already_applied(conn, job_url: str) -> bool:
    """
    Returns True only when a real (non-empty) URL has been seen before.
    Always returns False for empty strings so blank-URL rows are never blocked.
    """
    if not job_url:
        return False
    row = conn.execute(
        "SELECT 1 FROM applications WHERE job_url = ?", (job_url,)
    ).fetchone()
    return row is not None

def log_application(conn, job_title: str, company: str, platform: str,
                    status: str, reason: str = "", job_url: str = ""):
    """
    Log one application attempt to the database.

    job_url is optional — pass it when available to enable duplicate detection
    across sessions. When absent (empty string), the row is still recorded
    and the unique index is not triggered.
    """
    # Store None instead of "" so the partial unique index ignores it cleanly
    url_value = job_url if job_url else None
    try:
        conn.execute(
            "INSERT INTO applications VALUES (NULL,?,?,?,?,?,?,?)",
            (job_title, company, platform, status, reason, url_value,
             datetime.now().isoformat())
        )
        conn.commit()
    except sqlite3.IntegrityError:
        # A real duplicate URL was inserted twice — safe to skip
        pass

def daily_report(conn):
    """Returns a summary of today's applications grouped by platform and status."""
    return conn.execute("""
        SELECT platform, status, COUNT(*) as count
        FROM applications
        WHERE date(applied_at) = date('now')
        GROUP BY platform, status
        ORDER BY platform, status
    """).fetchall()

def all_time_report(conn):
    """Returns total application counts ever."""
    return conn.execute("""
        SELECT platform, status, COUNT(*) as count
        FROM applications
        GROUP BY platform, status
        ORDER BY platform, status
    """).fetchall()
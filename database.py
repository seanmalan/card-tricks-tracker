import sqlite3
import os
from datetime import date, timedelta


def get_db_path():
    # In Docker, DATA_DIR is set to a mounted volume (e.g. /data)
    # For local desktop use, falls back to ~/.card_tricks_tracker
    data_dir = os.environ.get("DATA_DIR")
    if not data_dir:
        data_dir = os.path.join(os.path.expanduser("~"), ".card_tricks_tracker")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, "tricks.db")


def get_connection():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            duration_mins INTEGER DEFAULT 0,
            title TEXT NOT NULL DEFAULT 'Practice Session',
            focus TEXT DEFAULT '',
            moves_practiced TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            rating INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS moves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT DEFAULT 'Other',
            level TEXT DEFAULT 'beginner',
            source TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            rating INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS tricks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT DEFAULT 'Trick',
            status TEXT DEFAULT 'learning',
            moves_used TEXT DEFAULT '',
            source TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            link TEXT DEFAULT '',
            rating INTEGER DEFAULT 0,
            last_practiced TEXT,
            practice_count INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('brush_up_days', '14')")

    conn.commit()
    conn.close()


# ---- HELPERS ----

def row_to_dict(row):
    return dict(row) if row else None

def rows_to_list(rows):
    return [dict(r) for r in rows]


# ---- SETTINGS ----

def get_all_settings():
    conn = get_connection()
    rows = conn.execute("SELECT key, value FROM settings").fetchall()
    conn.close()
    return {r["key"]: r["value"] for r in rows}

def set_setting(key, value):
    conn = get_connection()
    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    conn.close()


# ---- SESSIONS ----

def get_sessions():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM sessions ORDER BY date DESC, id DESC").fetchall()
    conn.close()
    return rows_to_list(rows)

def create_session(data):
    conn = get_connection()
    conn.execute(
        "INSERT INTO sessions (date, duration_mins, title, focus, moves_practiced, notes, rating, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            data["date"],
            data.get("duration", 0),
            data.get("title") or "Practice Session",
            data.get("focus", ""),
            data.get("moves_practiced", ""),
            data.get("notes", ""),
            data.get("rating", 0),
            date.today().isoformat(),
        ),
    )
    conn.commit()
    conn.close()

def delete_session(session_id):
    conn = get_connection()
    conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()


# ---- MOVES ----

def get_moves():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM moves ORDER BY name ASC").fetchall()
    conn.close()
    return rows_to_list(rows)

def upsert_move(data):
    conn = get_connection()
    now = date.today().isoformat()
    if data.get("id"):
        conn.execute(
            "UPDATE moves SET name=?, category=?, level=?, source=?, notes=?, rating=?, updated_at=? WHERE id=?",
            (data["name"], data.get("category","Other"), data.get("level","beginner"),
             data.get("source",""), data.get("notes",""), data.get("rating",0), now, data["id"]),
        )
    else:
        conn.execute(
            "INSERT INTO moves (name, category, level, source, notes, rating, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (data["name"], data.get("category","Other"), data.get("level","beginner"),
             data.get("source",""), data.get("notes",""), data.get("rating",0), now, now),
        )
    conn.commit()
    conn.close()

def delete_move(move_id):
    conn = get_connection()
    conn.execute("DELETE FROM moves WHERE id = ?", (move_id,))
    conn.commit()
    conn.close()


# ---- TRICKS ----

def get_tricks():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tricks ORDER BY name ASC").fetchall()
    conn.close()
    return rows_to_list(rows)

def upsert_trick(data):
    conn = get_connection()
    now = date.today().isoformat()
    if data.get("id"):
        conn.execute(
            "UPDATE tricks SET name=?, type=?, status=?, moves_used=?, source=?, notes=?, link=?, rating=?, updated_at=? WHERE id=?",
            (data["name"], data.get("type","Trick"), data.get("status","learning"),
             data.get("moves_used",""), data.get("source",""), data.get("notes",""),
             data.get("link",""), data.get("rating",0), now, data["id"]),
        )
    else:
        conn.execute(
            "INSERT INTO tricks (name, type, status, moves_used, source, notes, link, rating, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (data["name"], data.get("type","Trick"), data.get("status","learning"),
             data.get("moves_used",""), data.get("source",""), data.get("notes",""),
             data.get("link",""), data.get("rating",0), now, now),
        )
    conn.commit()
    conn.close()

def mark_trick_practiced(trick_id):
    conn = get_connection()
    conn.execute(
        "UPDATE tricks SET last_practiced=?, practice_count=practice_count+1, updated_at=? WHERE id=?",
        (date.today().isoformat(), date.today().isoformat(), trick_id),
    )
    conn.commit()
    conn.close()

def delete_trick(trick_id):
    conn = get_connection()
    conn.execute("DELETE FROM tricks WHERE id = ?", (trick_id,))
    conn.commit()
    conn.close()


# ---- DASHBOARD ----

def get_dashboard_data():
    conn = get_connection()

    settings = {r["key"]: r["value"] for r in conn.execute("SELECT key, value FROM settings").fetchall()}
    brush_up_days = int(settings.get("brush_up_days", 14))
    cutoff = (date.today() - timedelta(days=brush_up_days)).isoformat()

    total_sessions = conn.execute("SELECT COUNT(*) as c FROM sessions").fetchone()["c"]
    total_mins = conn.execute("SELECT COALESCE(SUM(duration_mins),0) as s FROM sessions").fetchone()["s"]
    total_moves = conn.execute("SELECT COUNT(*) as c FROM moves").fetchone()["c"]
    total_tricks = conn.execute("SELECT COUNT(*) as c FROM tricks").fetchone()["c"]
    perf_moves = conn.execute("SELECT COUNT(*) as c FROM moves WHERE level='performance'").fetchone()["c"]
    perf_tricks = conn.execute("SELECT COUNT(*) as c FROM tricks WHERE status='performance'").fetchone()["c"]

    last_session = conn.execute("SELECT date FROM sessions ORDER BY date DESC, id DESC LIMIT 1").fetchone()

    recent_sessions = rows_to_list(
        conn.execute("SELECT * FROM sessions ORDER BY date DESC, id DESC LIMIT 3").fetchall()
    )

    needs_brushup = rows_to_list(
        conn.execute(
            "SELECT * FROM tricks WHERE last_practiced IS NULL OR last_practiced <= ? "
            "ORDER BY last_practiced ASC NULLS FIRST LIMIT 5",
            (cutoff,),
        ).fetchall()
    )

    tricks_in_progress = rows_to_list(
        conn.execute(
            "SELECT * FROM tricks WHERE status IN ('learning','drilling') ORDER BY updated_at DESC LIMIT 5"
        ).fetchall()
    )

    moves_needing_work = rows_to_list(
        conn.execute(
            "SELECT * FROM moves WHERE level IN ('beginner','developing') ORDER BY updated_at DESC LIMIT 5"
        ).fetchall()
    )

    # 30-day chart: count sessions per day
    thirty_days = []
    today = date.today()
    for i in range(29, -1, -1):
        d = (today - timedelta(days=i)).isoformat()
        count = conn.execute(
            "SELECT COUNT(*) as c FROM sessions WHERE date = ?", (d,)
        ).fetchone()["c"]
        thirty_days.append({"date": d, "count": count})

    conn.close()

    avg_mins = round(total_mins / total_sessions) if total_sessions else 0

    return {
        "total_sessions": total_sessions,
        "total_hours": round(total_mins / 60, 1),
        "total_moves": total_moves,
        "total_tricks": total_tricks,
        "perf_moves": perf_moves,
        "perf_tricks": perf_tricks,
        "avg_mins": avg_mins,
        "last_session_date": last_session["date"] if last_session else None,
        "recent_sessions": recent_sessions,
        "needs_brushup": needs_brushup,
        "tricks_in_progress": tricks_in_progress,
        "moves_needing_work": moves_needing_work,
        "thirty_days": thirty_days,
        "brush_up_days": brush_up_days,
    }

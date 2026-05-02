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
        CREATE TABLE IF NOT EXISTS session_moves (
            session_id INTEGER NOT NULL,
            move_id INTEGER NOT NULL,
            PRIMARY KEY (session_id, move_id),
            FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
            FOREIGN KEY (move_id) REFERENCES moves(id) ON DELETE CASCADE
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS session_tricks (
            session_id INTEGER NOT NULL,
            trick_id INTEGER NOT NULL,
            PRIMARY KEY (session_id, trick_id),
            FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
            FOREIGN KEY (trick_id) REFERENCES tricks(id) ON DELETE CASCADE
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('brush_up_days', '14')")

    # Migrate: add last_practiced and practice_count to moves if not present
    for col, definition in [("last_practiced", "TEXT"), ("practice_count", "INTEGER DEFAULT 0")]:
        try:
            c.execute(f"ALTER TABLE moves ADD COLUMN {col} {definition}")
        except sqlite3.OperationalError:
            pass

    # Backfill: rows that pre-date the migration above have NULL practice_count.
    c.execute("UPDATE moves SET practice_count = 0 WHERE practice_count IS NULL")

    # Soft-delete columns. Active rows have deleted_at IS NULL.
    for table in ("sessions", "moves", "tricks"):
        try:
            c.execute(f"ALTER TABLE {table} ADD COLUMN deleted_at TEXT")
        except sqlite3.OperationalError:
            pass

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
    """Active sessions only. Linked moves/tricks include soft-deleted ones so
    historical session views don't lose context."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM sessions WHERE deleted_at IS NULL ORDER BY date DESC, id DESC"
    ).fetchall()

    moves_by_session = {}
    for r in conn.execute(
        "SELECT sm.session_id, m.id, m.name, m.category "
        "FROM session_moves sm JOIN moves m ON m.id = sm.move_id"
    ).fetchall():
        moves_by_session.setdefault(r["session_id"], []).append(
            {"id": r["id"], "name": r["name"], "category": r["category"]}
        )

    tricks_by_session = {}
    for r in conn.execute(
        "SELECT st.session_id, t.id, t.name, t.status "
        "FROM session_tricks st JOIN tricks t ON t.id = st.trick_id"
    ).fetchall():
        tricks_by_session.setdefault(r["session_id"], []).append(
            {"id": r["id"], "name": r["name"], "status": r["status"]}
        )

    result = []
    for row in rows:
        s = dict(row)
        s["linked_moves"] = moves_by_session.get(s["id"], [])
        s["linked_tricks"] = tricks_by_session.get(s["id"], [])
        result.append(s)
    conn.close()
    return result


def get_session(session_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM sessions WHERE id = ? AND deleted_at IS NULL",
        (session_id,),
    ).fetchone()
    if not row:
        conn.close()
        return None
    s = dict(row)
    s["linked_moves"] = rows_to_list(conn.execute(
        "SELECT m.id, m.name, m.category FROM moves m "
        "JOIN session_moves sm ON m.id = sm.move_id WHERE sm.session_id = ?",
        (session_id,),
    ).fetchall())
    s["linked_tricks"] = rows_to_list(conn.execute(
        "SELECT t.id, t.name, t.status FROM tricks t "
        "JOIN session_tricks st ON t.id = st.trick_id WHERE st.session_id = ?",
        (session_id,),
    ).fetchall())
    conn.close()
    return s

def create_session(data):
    """Insert a session and return its id with the linked-items dict."""
    conn = get_connection()
    today = date.today().isoformat()
    session_date = data["date"]
    c = conn.cursor()
    c.execute(
        "INSERT INTO sessions (date, duration_mins, title, focus, notes, rating, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            session_date,
            data.get("duration", 0),
            data.get("title") or "Practice Session",
            data.get("focus", ""),
            data.get("notes", ""),
            data.get("rating", 0),
            today,
        ),
    )
    session_id = c.lastrowid

    # last_practiced uses the session's date so backfilled sessions don't
    # falsely reset the brush-up clock to today.
    for move_id in data.get("move_ids", []):
        c.execute("INSERT OR IGNORE INTO session_moves (session_id, move_id) VALUES (?, ?)", (session_id, move_id))
        c.execute(
            "UPDATE moves SET "
            "last_practiced = CASE WHEN last_practiced IS NULL OR last_practiced < ? THEN ? ELSE last_practiced END, "
            "practice_count = practice_count + 1 "
            "WHERE id = ?",
            (session_date, session_date, move_id),
        )

    for trick_id in data.get("trick_ids", []):
        c.execute("INSERT OR IGNORE INTO session_tricks (session_id, trick_id) VALUES (?, ?)", (session_id, trick_id))
        c.execute(
            "UPDATE tricks SET "
            "last_practiced = CASE WHEN last_practiced IS NULL OR last_practiced < ? THEN ? ELSE last_practiced END, "
            "practice_count = practice_count + 1 "
            "WHERE id = ?",
            (session_date, session_date, trick_id),
        )

    conn.commit()
    conn.close()
    return session_id


def update_session(session_id, data):
    """Edit a session's date/duration/title/focus/notes/rating in place.

    Linked moves/tricks are not editable here (delete + re-create the session
    if you want to change those). If the date changes, last_practiced for any
    linked move/trick is rebuilt from the surviving sessions.
    """
    conn = get_connection()
    c = conn.cursor()
    existing = c.execute(
        "SELECT date FROM sessions WHERE id = ? AND deleted_at IS NULL",
        (session_id,),
    ).fetchone()
    if not existing:
        conn.close()
        return False

    old_date = existing["date"]
    new_date = data.get("date") or old_date
    c.execute(
        "UPDATE sessions SET date=?, duration_mins=?, title=?, focus=?, notes=?, rating=? WHERE id=?",
        (
            new_date,
            data.get("duration", 0),
            (data.get("title") or "Practice Session"),
            data.get("focus", ""),
            data.get("notes", ""),
            data.get("rating", 0),
            session_id,
        ),
    )

    if new_date != old_date:
        # Refresh last_practiced for everything this session is linked to.
        move_ids = [r[0] for r in c.execute(
            "SELECT move_id FROM session_moves WHERE session_id = ?", (session_id,)
        ).fetchall()]
        trick_ids = [r[0] for r in c.execute(
            "SELECT trick_id FROM session_tricks WHERE session_id = ?", (session_id,)
        ).fetchall()]
        for mid in move_ids:
            _refresh_move_last_practiced(c, mid)
        for tid in trick_ids:
            _refresh_trick_last_practiced(c, tid)

    conn.commit()
    conn.close()
    return True


def _refresh_move_last_practiced(c, move_id):
    latest = c.execute(
        "SELECT MAX(s.date) AS d FROM sessions s "
        "JOIN session_moves sm ON sm.session_id = s.id "
        "WHERE sm.move_id = ? AND s.deleted_at IS NULL",
        (move_id,),
    ).fetchone()
    c.execute("UPDATE moves SET last_practiced = ? WHERE id = ?", (latest["d"], move_id))


def _refresh_trick_last_practiced(c, trick_id):
    latest = c.execute(
        "SELECT MAX(s.date) AS d FROM sessions s "
        "JOIN session_tricks st ON st.session_id = s.id "
        "WHERE st.trick_id = ? AND s.deleted_at IS NULL",
        (trick_id,),
    ).fetchone()
    c.execute("UPDATE tricks SET last_practiced = ? WHERE id = ?", (latest["d"], trick_id))


def delete_session(session_id):
    """Soft-delete: marks the session as deleted, keeps history. Reverses
    practice_count and recomputes last_practiced for linked items."""
    conn = get_connection()

    sess = conn.execute(
        "SELECT date FROM sessions WHERE id = ? AND deleted_at IS NULL",
        (session_id,),
    ).fetchone()
    if not sess:
        conn.close()
        return
    session_date = sess["date"]

    move_ids = [r[0] for r in conn.execute(
        "SELECT move_id FROM session_moves WHERE session_id = ?", (session_id,)
    ).fetchall()]
    trick_ids = [r[0] for r in conn.execute(
        "SELECT trick_id FROM session_tricks WHERE session_id = ?", (session_id,)
    ).fetchall()]

    today = date.today().isoformat()
    conn.execute(
        "UPDATE sessions SET deleted_at = ? WHERE id = ?",
        (today, session_id),
    )

    c = conn.cursor()
    # Only adjust last_practiced when the deleted session's date matches the
    # currently stored value — that way a later session or out-of-band practice
    # mark on legacy data isn't clobbered.
    for mid in move_ids:
        c.execute("UPDATE moves SET practice_count = MAX(0, practice_count - 1) WHERE id = ?", (mid,))
        row = c.execute("SELECT last_practiced FROM moves WHERE id = ?", (mid,)).fetchone()
        if row and row["last_practiced"] == session_date:
            _refresh_move_last_practiced(c, mid)

    for tid in trick_ids:
        c.execute("UPDATE tricks SET practice_count = MAX(0, practice_count - 1) WHERE id = ?", (tid,))
        row = c.execute("SELECT last_practiced FROM tricks WHERE id = ?", (tid,)).fetchone()
        if row and row["last_practiced"] == session_date:
            _refresh_trick_last_practiced(c, tid)

    conn.commit()
    conn.close()


def restore_session(session_id):
    """Undo a soft-delete and bring practice_count / last_practiced back."""
    conn = get_connection()
    c = conn.cursor()
    sess = c.execute(
        "SELECT date FROM sessions WHERE id = ? AND deleted_at IS NOT NULL",
        (session_id,),
    ).fetchone()
    if not sess:
        conn.close()
        return False
    session_date = sess["date"]
    c.execute("UPDATE sessions SET deleted_at = NULL WHERE id = ?", (session_id,))

    move_ids = [r[0] for r in c.execute(
        "SELECT move_id FROM session_moves WHERE session_id = ?", (session_id,)
    ).fetchall()]
    trick_ids = [r[0] for r in c.execute(
        "SELECT trick_id FROM session_tricks WHERE session_id = ?", (session_id,)
    ).fetchall()]

    for mid in move_ids:
        c.execute("UPDATE moves SET practice_count = practice_count + 1 WHERE id = ?", (mid,))
        c.execute(
            "UPDATE moves SET last_practiced = ? "
            "WHERE id = ? AND (last_practiced IS NULL OR last_practiced < ?)",
            (session_date, mid, session_date),
        )

    for tid in trick_ids:
        c.execute("UPDATE tricks SET practice_count = practice_count + 1 WHERE id = ?", (tid,))
        c.execute(
            "UPDATE tricks SET last_practiced = ? "
            "WHERE id = ? AND (last_practiced IS NULL OR last_practiced < ?)",
            (session_date, tid, session_date),
        )

    conn.commit()
    conn.close()
    return True


# ---- MOVES ----

def get_moves():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM moves WHERE deleted_at IS NULL ORDER BY name ASC"
    ).fetchall()
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
        move_id = data["id"]
    else:
        c = conn.cursor()
        c.execute(
            "INSERT INTO moves (name, category, level, source, notes, rating, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (data["name"], data.get("category","Other"), data.get("level","beginner"),
             data.get("source",""), data.get("notes",""), data.get("rating",0), now, now),
        )
        move_id = c.lastrowid
    conn.commit()
    conn.close()
    return move_id

def delete_move(move_id):
    """Soft-delete the move (keeps existing session links intact)."""
    conn = get_connection()
    today = date.today().isoformat()
    conn.execute(
        "UPDATE moves SET deleted_at = ? WHERE id = ? AND deleted_at IS NULL",
        (today, move_id),
    )
    conn.commit()
    conn.close()

def restore_move(move_id):
    conn = get_connection()
    cur = conn.execute(
        "UPDATE moves SET deleted_at = NULL WHERE id = ? AND deleted_at IS NOT NULL",
        (move_id,),
    )
    n = cur.rowcount
    conn.commit()
    conn.close()
    return n > 0

def purge_move(move_id):
    """Permanently remove a soft-deleted move and its session links."""
    conn = get_connection()
    cur = conn.execute(
        "DELETE FROM moves WHERE id = ? AND deleted_at IS NOT NULL",
        (move_id,),
    )
    n = cur.rowcount
    conn.commit()
    conn.close()
    return n > 0


# ---- TRICKS ----

def get_tricks():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM tricks WHERE deleted_at IS NULL ORDER BY name ASC"
    ).fetchall()
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
        trick_id = data["id"]
    else:
        c = conn.cursor()
        c.execute(
            "INSERT INTO tricks (name, type, status, moves_used, source, notes, link, rating, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (data["name"], data.get("type","Trick"), data.get("status","learning"),
             data.get("moves_used",""), data.get("source",""), data.get("notes",""),
             data.get("link",""), data.get("rating",0), now, now),
        )
        trick_id = c.lastrowid
    conn.commit()
    conn.close()
    return trick_id

def mark_trick_practiced(trick_id):
    """Quick-log a practice for this trick by inserting a synthetic session
    (title 'Quick practice', duration 0). Idempotent within a single day —
    clicking the button twice on the same date does nothing the second time.

    Returns the session id if a session was created, or None if today already
    had one for this trick.
    """
    conn = get_connection()
    today = date.today().isoformat()
    c = conn.cursor()

    trick = c.execute(
        "SELECT id FROM tricks WHERE id = ? AND deleted_at IS NULL",
        (trick_id,),
    ).fetchone()
    if not trick:
        conn.close()
        return None

    existing = c.execute(
        "SELECT s.id FROM sessions s "
        "JOIN session_tricks st ON st.session_id = s.id "
        "WHERE st.trick_id = ? AND s.date = ? AND s.title = 'Quick practice' AND s.deleted_at IS NULL",
        (trick_id, today),
    ).fetchone()
    if existing:
        conn.close()
        return None

    c.execute(
        "INSERT INTO sessions (date, duration_mins, title, focus, notes, rating, created_at) "
        "VALUES (?, 0, 'Quick practice', '', 'Logged via ✓ Practiced Today', 0, ?)",
        (today, today),
    )
    session_id = c.lastrowid
    c.execute(
        "INSERT INTO session_tricks (session_id, trick_id) VALUES (?, ?)",
        (session_id, trick_id),
    )
    c.execute(
        "UPDATE tricks SET "
        "last_practiced = CASE WHEN last_practiced IS NULL OR last_practiced < ? THEN ? ELSE last_practiced END, "
        "practice_count = practice_count + 1, "
        "updated_at = ? "
        "WHERE id = ?",
        (today, today, today, trick_id),
    )
    conn.commit()
    conn.close()
    return session_id

def delete_trick(trick_id):
    """Soft-delete the trick (keeps existing session links intact)."""
    conn = get_connection()
    today = date.today().isoformat()
    conn.execute(
        "UPDATE tricks SET deleted_at = ? WHERE id = ? AND deleted_at IS NULL",
        (today, trick_id),
    )
    conn.commit()
    conn.close()

def restore_trick(trick_id):
    conn = get_connection()
    cur = conn.execute(
        "UPDATE tricks SET deleted_at = NULL WHERE id = ? AND deleted_at IS NOT NULL",
        (trick_id,),
    )
    n = cur.rowcount
    conn.commit()
    conn.close()
    return n > 0

def purge_trick(trick_id):
    """Permanently remove a soft-deleted trick and its session links."""
    conn = get_connection()
    cur = conn.execute(
        "DELETE FROM tricks WHERE id = ? AND deleted_at IS NOT NULL",
        (trick_id,),
    )
    n = cur.rowcount
    conn.commit()
    conn.close()
    return n > 0


# ---- TRASH / RESTORE ----

def get_deleted_items():
    """Everything currently soft-deleted, grouped by type."""
    conn = get_connection()
    sessions = rows_to_list(conn.execute(
        "SELECT id, date, title, deleted_at FROM sessions "
        "WHERE deleted_at IS NOT NULL ORDER BY deleted_at DESC LIMIT 50"
    ).fetchall())
    moves = rows_to_list(conn.execute(
        "SELECT id, name, category, deleted_at FROM moves "
        "WHERE deleted_at IS NOT NULL ORDER BY deleted_at DESC LIMIT 50"
    ).fetchall())
    tricks = rows_to_list(conn.execute(
        "SELECT id, name, type, deleted_at FROM tricks "
        "WHERE deleted_at IS NOT NULL ORDER BY deleted_at DESC LIMIT 50"
    ).fetchall())
    conn.close()
    return {"sessions": sessions, "moves": moves, "tricks": tricks}


# ---- HISTORY (per-item) ----

def get_move_history(move_id):
    conn = get_connection()
    move = conn.execute(
        "SELECT * FROM moves WHERE id = ? AND deleted_at IS NULL",
        (move_id,),
    ).fetchone()
    if not move:
        conn.close()
        return None
    sessions = rows_to_list(conn.execute(
        "SELECT s.id, s.date, s.title, s.duration_mins, s.rating "
        "FROM sessions s JOIN session_moves sm ON sm.session_id = s.id "
        "WHERE sm.move_id = ? AND s.deleted_at IS NULL "
        "ORDER BY s.date DESC, s.id DESC",
        (move_id,),
    ).fetchall())
    conn.close()
    return {"item": dict(move), "sessions": sessions}


def get_trick_history(trick_id):
    conn = get_connection()
    trick = conn.execute(
        "SELECT * FROM tricks WHERE id = ? AND deleted_at IS NULL",
        (trick_id,),
    ).fetchone()
    if not trick:
        conn.close()
        return None
    sessions = rows_to_list(conn.execute(
        "SELECT s.id, s.date, s.title, s.duration_mins, s.rating "
        "FROM sessions s JOIN session_tricks st ON st.session_id = s.id "
        "WHERE st.trick_id = ? AND s.deleted_at IS NULL "
        "ORDER BY s.date DESC, s.id DESC",
        (trick_id,),
    ).fetchall())
    conn.close()
    return {"item": dict(trick), "sessions": sessions}


# ---- EXPORT ----

def export_all():
    """Full database snapshot suitable for JSON serialisation. Includes
    soft-deleted rows so users have a complete backup."""
    conn = get_connection()
    payload = {
        "schema_version": 2,
        "exported_at": date.today().isoformat(),
        "sessions":  rows_to_list(conn.execute("SELECT * FROM sessions").fetchall()),
        "moves":     rows_to_list(conn.execute("SELECT * FROM moves").fetchall()),
        "tricks":    rows_to_list(conn.execute("SELECT * FROM tricks").fetchall()),
        "session_moves":  rows_to_list(conn.execute("SELECT * FROM session_moves").fetchall()),
        "session_tricks": rows_to_list(conn.execute("SELECT * FROM session_tricks").fetchall()),
        "settings":  rows_to_list(conn.execute("SELECT * FROM settings").fetchall()),
    }
    conn.close()
    return payload


# ---- DASHBOARD ----

def get_dashboard_data():
    conn = get_connection()

    settings = {r["key"]: r["value"] for r in conn.execute("SELECT key, value FROM settings").fetchall()}
    try:
        brush_up_days = int(settings.get("brush_up_days", 14))
        if brush_up_days < 1:
            brush_up_days = 14
    except (TypeError, ValueError):
        brush_up_days = 14
    cutoff = (date.today() - timedelta(days=brush_up_days)).isoformat()

    total_sessions = conn.execute("SELECT COUNT(*) as c FROM sessions WHERE deleted_at IS NULL").fetchone()["c"]
    total_mins = conn.execute("SELECT COALESCE(SUM(duration_mins),0) as s FROM sessions WHERE deleted_at IS NULL").fetchone()["s"]
    total_moves = conn.execute("SELECT COUNT(*) as c FROM moves WHERE deleted_at IS NULL").fetchone()["c"]
    total_tricks = conn.execute("SELECT COUNT(*) as c FROM tricks WHERE deleted_at IS NULL").fetchone()["c"]
    perf_moves = conn.execute("SELECT COUNT(*) as c FROM moves WHERE level='performance' AND deleted_at IS NULL").fetchone()["c"]
    perf_tricks = conn.execute("SELECT COUNT(*) as c FROM tricks WHERE status='performance' AND deleted_at IS NULL").fetchone()["c"]

    last_session = conn.execute(
        "SELECT date FROM sessions WHERE deleted_at IS NULL ORDER BY date DESC, id DESC LIMIT 1"
    ).fetchone()

    recent_sessions = rows_to_list(
        conn.execute("SELECT * FROM sessions WHERE deleted_at IS NULL ORDER BY date DESC, id DESC LIMIT 3").fetchall()
    )

    needs_brushup = rows_to_list(
        conn.execute(
            "SELECT * FROM tricks WHERE deleted_at IS NULL AND (last_practiced IS NULL OR last_practiced <= ?) "
            "ORDER BY last_practiced ASC NULLS FIRST LIMIT 5",
            (cutoff,),
        ).fetchall()
    )

    # Oldest practice first so the most overdue trick sits at the top of the
    # scrollable Tricks in Progress card.
    tricks_in_progress = rows_to_list(
        conn.execute(
            "SELECT * FROM tricks WHERE deleted_at IS NULL AND status IN ('learning','drilling') "
            "ORDER BY last_practiced ASC NULLS FIRST, updated_at DESC LIMIT 50"
        ).fetchall()
    )

    moves_needing_work = rows_to_list(
        conn.execute(
            "SELECT * FROM moves WHERE deleted_at IS NULL AND level IN ('beginner','developing') "
            "ORDER BY last_practiced ASC NULLS FIRST, updated_at DESC LIMIT 50"
        ).fetchall()
    )

    # 30-day chart: one GROUP BY query, then merge with the date range.
    today = date.today()
    start = (today - timedelta(days=29)).isoformat()
    counts = {
        r["date"]: r["c"]
        for r in conn.execute(
            "SELECT date, COUNT(*) AS c FROM sessions "
            "WHERE date >= ? AND deleted_at IS NULL GROUP BY date",
            (start,),
        ).fetchall()
    }
    thirty_days = [
        {"date": (today - timedelta(days=i)).isoformat(),
         "count": counts.get((today - timedelta(days=i)).isoformat(), 0)}
        for i in range(29, -1, -1)
    ]

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

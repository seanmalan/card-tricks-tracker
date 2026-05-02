"""Direct-API tests for database.py — covers the bug fixes plus the new
soft-delete / synthetic-session behaviour."""


def _add_move(db, name="Classic Pass"):
    return db.upsert_move({"name": name})


def _add_trick(db, name="Ambitious Card"):
    return db.upsert_trick({"name": name})


def test_init_creates_tables_and_default_settings(db):
    settings = db.get_all_settings()
    assert settings.get("brush_up_days") == "14"


def test_upsert_returns_new_id(db):
    mid = _add_move(db, "Riffle Pass")
    assert isinstance(mid, int) and mid > 0


def test_create_session_uses_session_date_for_last_practiced(db):
    mid = _add_move(db)
    db.create_session({"date": "2025-01-15", "duration": 30, "move_ids": [mid]})
    moves = db.get_moves()
    m = next(x for x in moves if x["id"] == mid)
    assert m["last_practiced"] == "2025-01-15"
    assert m["practice_count"] == 1


def test_backfill_session_does_not_overwrite_more_recent_last_practiced(db):
    mid = _add_move(db)
    db.create_session({"date": "2026-04-01", "move_ids": [mid]})
    db.create_session({"date": "2025-01-15", "move_ids": [mid]})  # backfilled
    m = next(x for x in db.get_moves() if x["id"] == mid)
    assert m["last_practiced"] == "2026-04-01"
    assert m["practice_count"] == 2


def test_delete_session_recomputes_last_practiced(db):
    mid = _add_move(db)
    sid_old = db.create_session({"date": "2025-01-15", "move_ids": [mid]})
    sid_new = db.create_session({"date": "2026-04-01", "move_ids": [mid]})
    db.delete_session(sid_new)
    m = next(x for x in db.get_moves() if x["id"] == mid)
    assert m["last_practiced"] == "2025-01-15"
    assert m["practice_count"] == 1


def test_soft_delete_session_keeps_row(db):
    mid = _add_move(db)
    sid = db.create_session({"date": "2026-01-01", "move_ids": [mid]})
    db.delete_session(sid)
    assert db.get_sessions() == []
    trash = db.get_deleted_items()
    assert any(s["id"] == sid for s in trash["sessions"])


def test_restore_session_brings_back_practice_count(db):
    mid = _add_move(db)
    sid = db.create_session({"date": "2026-01-01", "move_ids": [mid]})
    db.delete_session(sid)
    assert db.restore_session(sid) is True
    assert any(s["id"] == sid for s in db.get_sessions())
    m = next(x for x in db.get_moves() if x["id"] == mid)
    assert m["practice_count"] == 1
    assert m["last_practiced"] == "2026-01-01"


def test_soft_delete_move_then_restore(db):
    mid = _add_move(db, "Hindu Pass")
    db.delete_move(mid)
    assert all(m["id"] != mid for m in db.get_moves())
    assert mid in [m["id"] for m in db.get_deleted_items()["moves"]]
    assert db.restore_move(mid) is True
    assert any(m["id"] == mid for m in db.get_moves())


def test_purge_move_only_works_on_trashed(db):
    mid = _add_move(db)
    assert db.purge_move(mid) is False  # active, not in trash
    db.delete_move(mid)
    assert db.purge_move(mid) is True


def test_mark_trick_practiced_creates_synthetic_session_idempotently(db):
    tid = _add_trick(db)
    sid1 = db.mark_trick_practiced(tid)
    sid2 = db.mark_trick_practiced(tid)  # same day → no new session
    assert isinstance(sid1, int)
    assert sid2 is None
    sessions = db.get_sessions()
    quick = [s for s in sessions if s["title"] == "Quick practice"]
    assert len(quick) == 1
    t = next(x for x in db.get_tricks() if x["id"] == tid)
    assert t["practice_count"] == 1
    assert t["last_practiced"] is not None


def test_brush_up_days_falls_back_on_bad_value(db):
    db.set_setting("brush_up_days", "not-a-number")
    data = db.get_dashboard_data()
    assert data["brush_up_days"] == 14


def test_dashboard_excludes_deleted(db):
    mid = _add_move(db, "Will Be Deleted")
    db.delete_move(mid)
    data = db.get_dashboard_data()
    assert data["total_moves"] == 0


def test_history_returns_sessions(db):
    tid = _add_trick(db)
    db.create_session({"date": "2026-04-01", "trick_ids": [tid], "duration": 20})
    db.create_session({"date": "2026-04-02", "trick_ids": [tid], "duration": 15})
    h = db.get_trick_history(tid)
    assert len(h["sessions"]) == 2
    assert h["sessions"][0]["date"] == "2026-04-02"  # most recent first


def test_export_includes_all_tables(db):
    _add_move(db)
    _add_trick(db)
    payload = db.export_all()
    for k in ("sessions", "moves", "tricks", "session_moves", "session_tricks", "settings"):
        assert k in payload


def test_update_session_changes_date_and_refreshes_last_practiced(db):
    mid = _add_move(db)
    sid = db.create_session({"date": "2026-04-01", "move_ids": [mid]})
    assert db.update_session(sid, {"date": "2026-04-10"}) is True
    m = next(x for x in db.get_moves() if x["id"] == mid)
    assert m["last_practiced"] == "2026-04-10"

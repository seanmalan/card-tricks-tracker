"""Verifies the dad-bug fix: seed runs once then stays out of the way."""
import sqlite3


def _connect(db):
    return sqlite3.connect(db.get_db_path())


def test_seed_runs_once_then_skips(db, capsys):
    import importlib, seed
    importlib.reload(seed)
    seed.run_seed()
    n_moves_first = _connect(db).execute("SELECT COUNT(*) FROM moves").fetchone()[0]
    assert n_moves_first > 0

    # Simulate user deleting some seeded rows, then a container restart.
    _connect(db).execute("DELETE FROM moves WHERE name = 'Classic Pass'").connection.commit()
    seed.run_seed()
    rows = _connect(db).execute("SELECT COUNT(*) FROM moves WHERE name = 'Classic Pass'").fetchone()[0]
    assert rows == 0, "seed should NOT re-add deleted rows on restart"


def test_seed_skips_when_existing_data_present(db):
    """Pre-existing data without the seed flag (e.g. an older install) should
    NOT trigger the starter library a second time."""
    import importlib, seed
    importlib.reload(seed)
    db.upsert_move({"name": "My Custom Move"})
    seed.run_seed()
    moves = db.get_moves()
    names = [m["name"] for m in moves]
    assert "My Custom Move" in names
    # Starter content should NOT have been added.
    assert "Classic Pass" not in names


def test_dedupe_seed_duplicates(db):
    """If a database already has duplicates from the old buggy seed,
    --dedupe collapses them while marking the seed flag."""
    import importlib, seed
    importlib.reload(seed)
    db.upsert_move({"name": "Classic Pass"})
    db.upsert_move({"name": "Classic Pass"})
    db.upsert_move({"name": "Classic Pass"})
    seed.dedupe_seed_duplicates()
    rows = _connect(db).execute(
        "SELECT COUNT(*) FROM moves WHERE name = 'Classic Pass'"
    ).fetchone()[0]
    assert rows == 1
    flag = _connect(db).execute(
        "SELECT value FROM settings WHERE key = 'initial_seed_done'"
    ).fetchone()[0]
    assert flag == "1"


def test_remove_untouched_seeds_removes_clean_starters(db):
    import importlib, seed
    importlib.reload(seed)
    seed.run_seed()
    seed.remove_untouched_seeds()
    moves = db.get_moves()
    tricks = db.get_tricks()
    assert moves == [], "all starter moves were untouched and should be gone"
    assert tricks == [], "all starter tricks were untouched and should be gone"


def test_seed_starter_notes_fills_only_empty_notes(db):
    import importlib, seed
    importlib.reload(seed)
    seed.run_seed()

    # User has written their own notes on Triumph
    tricks_before = db.get_tricks()
    triumph = next(t for t in tricks_before if t["name"] == "Triumph")
    db.upsert_trick({"id": triumph["id"], "name": "Triumph", "notes": "MY OWN HANDLING"})

    seed.seed_starter_notes()
    tricks_after = db.get_tricks()
    triumph_after = next(t for t in tricks_after if t["name"] == "Triumph")
    ambitious_after = next(t for t in tricks_after if t["name"] == "Ambitious Card")

    assert triumph_after["notes"] == "MY OWN HANDLING", "user notes must not be overwritten"
    assert "Ambitious Card" in ambitious_after["notes"] or "EFFECT" in ambitious_after["notes"], \
        "empty notes should now have starter content"


def test_remove_untouched_seeds_preserves_user_changes(db):
    import importlib, seed
    importlib.reload(seed)
    seed.run_seed()

    # Touch a few rows in different ways
    moves = db.get_moves()
    tricks = db.get_tricks()
    rated = next(m for m in moves if m["name"] == "Classic Pass")
    noted = next(m for m in moves if m["name"] == "Classic Force")
    practiced_trick = next(t for t in tricks if t["name"] == "Triumph")
    statused_trick = next(t for t in tricks if t["name"] == "Ambitious Card")

    db.upsert_move({"id": rated["id"], "name": rated["name"], "rating": 4})
    db.upsert_move({"id": noted["id"], "name": noted["name"], "notes": "feels solid"})
    db.create_session({"date": "2026-04-01", "trick_ids": [practiced_trick["id"]]})
    db.upsert_trick({"id": statused_trick["id"], "name": statused_trick["name"], "status": "drilling"})

    # And add a custom move the seed has never heard of
    db.upsert_move({"name": "My Custom Cull"})

    seed.remove_untouched_seeds()

    surviving_moves = {m["name"] for m in db.get_moves()}
    surviving_tricks = {t["name"] for t in db.get_tricks()}

    assert "Classic Pass" in surviving_moves         # rated → kept
    assert "Classic Force" in surviving_moves        # has notes → kept
    assert "My Custom Cull" in surviving_moves       # not a seed name → kept
    assert "Triumph" in surviving_tricks             # practiced → kept
    assert "Ambitious Card" in surviving_tricks      # status changed → kept

    # Untouched seeds should have been swept
    assert "Riffle Pass" not in surviving_moves
    assert "Out of This World" not in surviving_tricks

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

"""Pytest fixtures: each test gets a fresh, empty SQLite database in a
tempdir so tests can't leak state into each other."""
import os
import sys
import tempfile

import pytest

# Make the repo root importable when pytest is invoked from anywhere.
_HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)


@pytest.fixture
def data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    return tmp_path


@pytest.fixture
def db(data_dir):
    """Initialised database module pointed at a fresh DB."""
    import importlib
    import database
    importlib.reload(database)  # picks up the new DATA_DIR
    database.init_db()
    return database


@pytest.fixture
def client(db):
    import importlib
    import app as app_module
    importlib.reload(app_module)
    flask_app = app_module.create_app()
    flask_app.config["TESTING"] = True
    return flask_app.test_client()

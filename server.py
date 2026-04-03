"""
Entry point for the Docker container.
Runs Flask on 0.0.0.0 so it's reachable across the local network.
Seeds the database with starter moves and tricks on first run.
"""
from app import create_app
from database import init_db
import seed  # noqa: F401 — runs INSERT OR IGNORE seed on import

if __name__ == "__main__":
    init_db()
    app = create_app()
    app.run(host="0.0.0.0", port=5757, debug=False)

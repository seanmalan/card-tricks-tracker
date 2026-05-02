"""
Entry point for the Docker container.
Runs the Flask app via waitress on 0.0.0.0 so it's reachable across the LAN.
Seeds the database with starter moves and tricks on first run.
"""
from waitress import serve

from app import create_app
from database import init_db
from seed import run_seed

PORT = 5757

if __name__ == "__main__":
    init_db()
    run_seed()
    app = create_app()
    serve(app, host="0.0.0.0", port=PORT, threads=8)

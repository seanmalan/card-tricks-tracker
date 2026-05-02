"""
Entry point for the Docker container.
Runs the Flask app via waitress on 0.0.0.0 so it's reachable across the LAN.

The starter library is NOT auto-seeded — it ships only as a manual tool
(`python3 seed.py`) because previous auto-seed behaviour kept re-introducing
rows the user had deleted.
"""
from waitress import serve

from app import create_app
from database import init_db

PORT = 5757

if __name__ == "__main__":
    init_db()
    app = create_app()
    serve(app, host="0.0.0.0", port=PORT, threads=8)

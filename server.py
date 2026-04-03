"""
Entry point for the Docker container.
Runs Flask on 0.0.0.0 so it's reachable across the local network.
"""
from app import create_app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5757, debug=False)

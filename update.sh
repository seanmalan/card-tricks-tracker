#!/usr/bin/env bash
# Card Shark — one-shot update script for Mac/Linux.
# Pulls the latest code, rebuilds the Docker image, and restarts the app.
set -e
cd "$(dirname "$0")"

echo "→ pulling latest code from GitHub..."
git pull

echo "→ stopping running container..."
docker compose down

echo "→ rebuilding image and starting..."
docker compose up -d --build

echo
echo "Done. Open http://localhost:5757 in your browser."

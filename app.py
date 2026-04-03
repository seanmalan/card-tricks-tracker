import os
import sys
from flask import Flask, jsonify, request, send_from_directory

import database as db


def create_app():
    # Handle PyInstaller bundled path for static files
    if getattr(sys, "frozen", False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    static_dir = os.path.join(base_dir, "static")
    app = Flask(__name__, static_folder=static_dir)

    db.init_db()

    # ---- Serve frontend ----

    @app.route("/")
    def index():
        return send_from_directory(static_dir, "index.html")

    # ---- Dashboard ----

    @app.route("/api/dashboard")
    def dashboard():
        return jsonify(db.get_dashboard_data())

    # ---- Sessions ----

    @app.route("/api/sessions", methods=["GET"])
    def get_sessions():
        return jsonify(db.get_sessions())

    @app.route("/api/sessions", methods=["POST"])
    def create_session():
        db.create_session(request.json)
        return jsonify({"ok": True})

    @app.route("/api/sessions/<int:session_id>", methods=["DELETE"])
    def delete_session(session_id):
        db.delete_session(session_id)
        return jsonify({"ok": True})

    # ---- Moves ----

    @app.route("/api/moves", methods=["GET"])
    def get_moves():
        return jsonify(db.get_moves())

    @app.route("/api/moves", methods=["POST"])
    def upsert_move():
        db.upsert_move(request.json)
        return jsonify({"ok": True})

    @app.route("/api/moves/<int:move_id>", methods=["DELETE"])
    def delete_move(move_id):
        db.delete_move(move_id)
        return jsonify({"ok": True})

    # ---- Tricks ----

    @app.route("/api/tricks", methods=["GET"])
    def get_tricks():
        return jsonify(db.get_tricks())

    @app.route("/api/tricks", methods=["POST"])
    def upsert_trick():
        db.upsert_trick(request.json)
        return jsonify({"ok": True})

    @app.route("/api/tricks/<int:trick_id>/practiced", methods=["POST"])
    def mark_practiced(trick_id):
        db.mark_trick_practiced(trick_id)
        return jsonify({"ok": True})

    @app.route("/api/tricks/<int:trick_id>", methods=["DELETE"])
    def delete_trick(trick_id):
        db.delete_trick(trick_id)
        return jsonify({"ok": True})

    # ---- Settings ----

    @app.route("/api/settings", methods=["GET"])
    def get_settings():
        return jsonify(db.get_all_settings())

    @app.route("/api/settings", methods=["POST"])
    def update_setting():
        data = request.json
        db.set_setting(data["key"], data["value"])
        return jsonify({"ok": True})

    return app

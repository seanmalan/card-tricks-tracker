import csv
import io
import json
import logging
import os
import sys
from flask import Flask, Response, jsonify, request, send_from_directory

import database as db


log = logging.getLogger(__name__)


def _json_body():
    """Return parsed JSON body or raise a 400-friendly ValueError."""
    data = request.get_json(silent=True)
    if data is None:
        raise ValueError("Request body must be valid JSON with Content-Type: application/json")
    return data


def create_app():
    # Handle PyInstaller bundled path for static files
    if getattr(sys, "frozen", False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    static_dir = os.path.join(base_dir, "static")
    app = Flask(__name__, static_folder=static_dir)

    db.init_db()

    @app.errorhandler(Exception)
    def handle_unexpected(err):
        # ValueError → 400 (bad input). Everything else → 500 with logged trace.
        if isinstance(err, ValueError):
            return jsonify({"ok": False, "error": str(err)}), 400
        log.exception("Unhandled error in request")
        return jsonify({"ok": False, "error": "Internal server error"}), 500

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

    @app.route("/api/sessions/<int:session_id>", methods=["GET"])
    def get_session(session_id):
        sess = db.get_session(session_id)
        if not sess:
            return jsonify({"ok": False, "error": "Session not found"}), 404
        return jsonify(sess)

    @app.route("/api/sessions", methods=["POST"])
    def create_session():
        data = _json_body()
        if not data.get("date"):
            raise ValueError("Session date is required")
        sid = db.create_session(data)
        return jsonify({"ok": True, "id": sid})

    @app.route("/api/sessions/<int:session_id>", methods=["PUT"])
    def update_session(session_id):
        data = _json_body()
        if not data.get("date"):
            raise ValueError("Session date is required")
        if not db.update_session(session_id, data):
            return jsonify({"ok": False, "error": "Session not found"}), 404
        return jsonify({"ok": True})

    @app.route("/api/sessions/<int:session_id>", methods=["DELETE"])
    def delete_session(session_id):
        db.delete_session(session_id)
        return jsonify({"ok": True})

    @app.route("/api/sessions/<int:session_id>/restore", methods=["POST"])
    def restore_session(session_id):
        if not db.restore_session(session_id):
            return jsonify({"ok": False, "error": "Session not in trash"}), 404
        return jsonify({"ok": True})

    # ---- Moves ----

    @app.route("/api/moves", methods=["GET"])
    def get_moves():
        return jsonify(db.get_moves())

    @app.route("/api/moves", methods=["POST"])
    def upsert_move():
        data = _json_body()
        if not (data.get("name") or "").strip():
            raise ValueError("Move name is required")
        mid = db.upsert_move(data)
        return jsonify({"ok": True, "id": mid})

    @app.route("/api/moves/<int:move_id>", methods=["DELETE"])
    def delete_move(move_id):
        db.delete_move(move_id)
        return jsonify({"ok": True})

    @app.route("/api/moves/<int:move_id>/restore", methods=["POST"])
    def restore_move(move_id):
        if not db.restore_move(move_id):
            return jsonify({"ok": False, "error": "Move not in trash"}), 404
        return jsonify({"ok": True})

    @app.route("/api/moves/<int:move_id>/purge", methods=["DELETE"])
    def purge_move(move_id):
        if not db.purge_move(move_id):
            return jsonify({"ok": False, "error": "Move not in trash"}), 404
        return jsonify({"ok": True})

    @app.route("/api/moves/<int:move_id>/history", methods=["GET"])
    def move_history(move_id):
        h = db.get_move_history(move_id)
        if not h:
            return jsonify({"ok": False, "error": "Move not found"}), 404
        return jsonify(h)

    # ---- Tricks ----

    @app.route("/api/tricks", methods=["GET"])
    def get_tricks():
        return jsonify(db.get_tricks())

    @app.route("/api/tricks", methods=["POST"])
    def upsert_trick():
        data = _json_body()
        if not (data.get("name") or "").strip():
            raise ValueError("Trick name is required")
        tid = db.upsert_trick(data)
        return jsonify({"ok": True, "id": tid})

    @app.route("/api/tricks/<int:trick_id>/practiced", methods=["POST"])
    def mark_practiced(trick_id):
        sid = db.mark_trick_practiced(trick_id)
        return jsonify({"ok": True, "session_id": sid})

    @app.route("/api/tricks/<int:trick_id>", methods=["DELETE"])
    def delete_trick(trick_id):
        db.delete_trick(trick_id)
        return jsonify({"ok": True})

    @app.route("/api/tricks/<int:trick_id>/restore", methods=["POST"])
    def restore_trick(trick_id):
        if not db.restore_trick(trick_id):
            return jsonify({"ok": False, "error": "Trick not in trash"}), 404
        return jsonify({"ok": True})

    @app.route("/api/tricks/<int:trick_id>/purge", methods=["DELETE"])
    def purge_trick(trick_id):
        if not db.purge_trick(trick_id):
            return jsonify({"ok": False, "error": "Trick not in trash"}), 404
        return jsonify({"ok": True})

    @app.route("/api/tricks/<int:trick_id>/history", methods=["GET"])
    def trick_history(trick_id):
        h = db.get_trick_history(trick_id)
        if not h:
            return jsonify({"ok": False, "error": "Trick not found"}), 404
        return jsonify(h)

    # ---- Trash / Restore ----

    @app.route("/api/trash", methods=["GET"])
    def list_trash():
        return jsonify(db.get_deleted_items())

    # ---- Export ----

    @app.route("/api/export", methods=["GET"])
    def export_data():
        fmt = (request.args.get("format") or "json").lower()
        payload = db.export_all()
        stamp = payload["exported_at"]

        if fmt == "json":
            body = json.dumps(payload, indent=2)
            return Response(
                body,
                mimetype="application/json",
                headers={"Content-Disposition": f'attachment; filename="prestige-export-{stamp}.json"'},
            )

        if fmt == "csv":
            buf = io.StringIO()
            for table in ("sessions", "moves", "tricks", "session_moves", "session_tricks", "settings"):
                rows = payload[table]
                buf.write(f"# {table}\n")
                if rows:
                    fields = list(rows[0].keys())
                    w = csv.DictWriter(buf, fieldnames=fields)
                    w.writeheader()
                    for r in rows:
                        w.writerow(r)
                buf.write("\n")
            return Response(
                buf.getvalue(),
                mimetype="text/csv",
                headers={"Content-Disposition": f'attachment; filename="prestige-export-{stamp}.csv"'},
            )

        raise ValueError("format must be 'json' or 'csv'")

    # ---- Settings ----

    @app.route("/api/settings", methods=["GET"])
    def get_settings():
        return jsonify(db.get_all_settings())

    @app.route("/api/settings", methods=["POST"])
    def update_setting():
        data = _json_body()
        key = data.get("key")
        if not key:
            raise ValueError("Setting key is required")
        db.set_setting(key, data.get("value", ""))
        return jsonify({"ok": True})

    return app

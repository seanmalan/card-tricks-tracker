"""HTTP-level tests against Flask's test client."""


def test_dashboard_endpoint(client):
    r = client.get("/api/dashboard")
    assert r.status_code == 200
    assert r.get_json()["total_sessions"] == 0


def test_post_session_requires_json_content_type(client):
    r = client.post("/api/sessions", data="oops", headers={"Content-Type": "text/plain"})
    assert r.status_code == 400
    assert r.get_json()["ok"] is False


def test_post_move_requires_name(client):
    r = client.post("/api/moves", json={"category": "Other"})
    assert r.status_code == 400
    assert "name" in r.get_json()["error"].lower()


def test_create_and_edit_session(client):
    mr = client.post("/api/moves", json={"name": "Top Change"})
    mid = mr.get_json()["id"]
    sr = client.post("/api/sessions", json={"date": "2026-04-01", "duration": 25, "move_ids": [mid]})
    sid = sr.get_json()["id"]
    er = client.put(f"/api/sessions/{sid}", json={"date": "2026-04-05", "duration": 40})
    assert er.status_code == 200
    g = client.get(f"/api/sessions/{sid}")
    assert g.get_json()["date"] == "2026-04-05"
    assert g.get_json()["duration_mins"] == 40


def test_soft_delete_then_restore_via_api(client):
    mr = client.post("/api/moves", json={"name": "Side Steal"})
    mid = mr.get_json()["id"]
    client.delete(f"/api/moves/{mid}")
    moves = client.get("/api/moves").get_json()
    assert all(m["id"] != mid for m in moves)
    trash = client.get("/api/trash").get_json()
    assert mid in [m["id"] for m in trash["moves"]]
    client.post(f"/api/moves/{mid}/restore")
    moves = client.get("/api/moves").get_json()
    assert any(m["id"] == mid for m in moves)


def test_practiced_today_creates_session(client):
    tr = client.post("/api/tricks", json={"name": "Triumph"})
    tid = tr.get_json()["id"]
    r = client.post(f"/api/tricks/{tid}/practiced")
    assert r.status_code == 200
    assert r.get_json()["session_id"] is not None
    sessions = client.get("/api/sessions").get_json()
    assert any(s["title"] == "Quick practice" for s in sessions)


def test_export_json(client):
    r = client.get("/api/export?format=json")
    assert r.status_code == 200
    assert r.headers["Content-Type"].startswith("application/json")
    assert r.headers["Content-Disposition"].startswith("attachment")
    payload = r.get_json()
    assert "sessions" in payload


def test_export_csv(client):
    r = client.get("/api/export?format=csv")
    assert r.status_code == 200
    assert r.headers["Content-Type"].startswith("text/csv")
    assert b"# sessions" in r.data


def test_export_rejects_bad_format(client):
    r = client.get("/api/export?format=xml")
    assert r.status_code == 400


def test_history_endpoints(client):
    tr = client.post("/api/tricks", json={"name": "Card Warp"})
    tid = tr.get_json()["id"]
    client.post("/api/sessions", json={"date": "2026-04-01", "trick_ids": [tid]})
    h = client.get(f"/api/tricks/{tid}/history").get_json()
    assert len(h["sessions"]) == 1
    bad = client.get("/api/tricks/99999/history")
    assert bad.status_code == 404

"""Tests for Subsystem 4 - Web App, Dashboard & Integration (Vijay).

Uses Flask's test client (no real server) with a fake detector and fake LLM.
"""

from conftest import FakeDetector, FakeLLM, login, make_image_bytes, register
from subsystem_4_web_integration import (AppConfig, MissingUploadError, ValidationFailedError,
                                         WebDashboardErrorHandler)


def upload(client, data=None, threshold="50"):
    from io import BytesIO
    payload = {"threshold": threshold}
    if data is not None:
        payload["photo"] = (BytesIO(data), "photo.png")
    return client.post("/api/analyze", data=payload, content_type="multipart/form-data")


def test_health_needs_no_login(build_client):
    response = build_client().get("/health")
    assert response.status_code == 200 and response.get_json()["status"] == "ok"


def test_anonymous_users_are_redirected_or_rejected(build_client):
    c = build_client()
    assert c.get("/").headers["Location"].endswith("/login")
    assert c.post("/api/analyze").status_code == 401


def test_login_logout_flow(build_client):
    c = build_client()
    assert login(c, password="wrong").status_code == 200           # form shown again with an error
    assert b"Incorrect username, password or role" in login(c, password="wrong").data
    assert login(c, role="admin").status_code == 302
    assert c.get("/").status_code == 200
    c.post("/logout")
    assert c.get("/").status_code == 302


def test_signup_checks_invitation_code(build_client):
    c = build_client()
    bad = c.post("/signup", data={"username": "anna", "password": "secret1", "role": "user", "signup_code": "x"})
    assert b"invitation code is incorrect" in bad.data
    ok = c.post("/signup", data={"username": "anna", "password": "secret1", "role": "user", "signup_code": "pythonai"})
    assert ok.status_code == 302 and login(c, "anna", "secret1").status_code == 302


def test_analyze_confident_photo(client):
    body = upload(client, make_image_bytes()).get_json()
    assert body["top"]["label"] == "Plastic" and body["needs_review"] is False
    assert body["route"]["bin_de"] and "job_id" not in body


def test_analyze_low_confidence_starts_review(build_client):
    c = build_client(detector=FakeDetector("Glass", 0.3), llm=FakeLLM(answer="Use the Blue paper bin"))
    login(c)
    body = upload(c, make_image_bytes()).get_json()
    assert body["needs_review"] and "job_id" in body
    job = c.get(f"/api/review/{body['job_id']}").get_json()
    assert job["status"] == "done" and job["source"] == "llm" and job["label"] == "Papier"


def test_review_falls_back_without_api_key(build_client):
    c = build_client(detector=FakeDetector("Glass", 0.3), llm=FakeLLM(configured=False))
    login(c)
    job_id = upload(c, make_image_bytes()).get_json()["job_id"]
    assert c.get(f"/api/review/{job_id}").get_json()["source"] == "local-fallback"


def test_missing_and_corrupt_uploads_give_safe_errors(client):
    missing = upload(client)
    assert missing.status_code == 400 and "photo" in missing.get_json()["error"].lower()
    corrupt = upload(client, b"garbage-bytes")
    assert corrupt.status_code == 400 and "Traceback" not in corrupt.get_data(as_text=True)


def test_model_failure_returns_safe_500(build_client):
    c = build_client(detector=FakeDetector(fail=True))
    login(c)
    response = upload(c, make_image_bytes())
    assert response.status_code == 500 and "boom" not in response.get_data(as_text=True)


def test_chat_with_llm_and_without_key(build_client):
    c = build_client(llm=FakeLLM(answer="Batteries go to a collection point."))
    login(c)
    reply = c.post("/api/chat", json={"message": "battery?"}).get_json()
    assert "collection point" in reply["answer"]
    assert c.post("/api/chat", json={"message": ""}).status_code == 400
    c2 = build_client(llm=FakeLLM(configured=False))
    login(c2)
    assert c2.post("/api/chat", json={"message": "hi"}).status_code == 503


def test_admin_can_edit_rules_users_cannot(build_client):
    admin = build_client(); login(admin)
    rule = admin.get("/api/dashboard/stats").get_json()   # smoke: stats work before edits
    assert rule["totals"]["scans"] == 0
    payload = {"label": "Glass", "category": "Glass", "bin": "Edited bin", "bin_de": "Neu", "color": "Green",
               "hex": "#00aa00", "theme": "glass", "symbol": "bottle", "note": "Edited note"}
    assert admin.post("/api/admin/rules", json=payload).status_code == 200
    assert b"Edited bin" in admin.get("/admin/rules").data
    admin.post("/signup", data={"username": "bob", "password": "secret1", "role": "user", "signup_code": "pythonai"})
    user = build_client(); login(user, "bob", "secret1")
    assert user.post("/api/admin/rules", json=payload).status_code == 403


def test_dashboard_stats_history_and_csv(client):
    upload(client, make_image_bytes())
    stats = client.get("/api/dashboard/stats").get_json()
    assert stats["totals"]["scans"] == 1 and stats["by_bin"][0]["label"] == "Plastic"
    assert client.get("/api/dashboard/stats?waste=Glass").get_json()["totals"]["scans"] == 0
    assert client.get("/history").status_code == 200 and client.get("/dashboard").status_code == 200
    assert "Plastic" in client.get("/api/dashboard/export.csv").get_data(as_text=True)


def test_photo_route_blocks_path_tricks(client):
    assert client.get("/api/photo/..%2Fsortly.sqlite3").status_code == 404
    assert client.get("/api/photo/notes.txt").status_code == 404


def test_tunnel_is_disabled_in_docker_style_config(client):
    state = client.get("/api/tunnel/status").get_json()
    assert state["status"] == "disabled" and client.post("/api/tunnel/start").status_code == 503


def test_config_describe_never_leaks_key():
    config = AppConfig.from_cli(["--api-key", "top-secret", "--port", "7000", "--no-browser"])
    assert config.port == 7000 and "top-secret" not in str(config.describe())


def test_error_handler_for_web_errors():
    handler = WebDashboardErrorHandler()
    assert handler.handle(MissingUploadError()).http_status == 400
    assert handler.handle(ValidationFailedError("Pick a name")).message == "Pick a name"
    assert handler.handle(RuntimeError("secret db path")).message == "Something went wrong. Please try again."


# ---------------------------------------------------------------- roles and permissions
def test_login_role_must_match_account(build_client):
    c = build_client()
    register(c, "mia", "user")
    assert b"Incorrect username, password or role" in login(c, "mia", "secret1", role="admin").data   # no privilege escalation
    assert login(c, "mia", "secret1", role="user").status_code == 302


def test_normal_user_gets_assistant_only(build_client):
    c = build_client(); register(c, "uma", "user"); login(c, "uma", "secret1", role="user")
    assert c.get("/").status_code == 200
    for page in ("/history", "/dashboard", "/admin/rules"):
        assert c.get(page).headers["Location"].endswith("/")          # redirected home
    for api in ("/api/dashboard/stats", "/api/dashboard/export.csv", "/api/tunnel/status"):
        assert c.get(api).status_code == 403
    assert c.post("/api/tunnel/start").status_code == 403
    assert b"Dashboard" not in c.get("/").data and b"Go live" not in c.get("/").data


def test_municipality_sees_dashboard_but_not_history(build_client):
    c = build_client(); register(c, "max", "municipality"); login(c, "max", "secret1", role="municipality")
    assert c.get("/dashboard").status_code == 200
    assert c.get("/api/dashboard/stats").status_code == 200
    assert c.get("/history").status_code == 302
    assert c.get("/api/dashboard/export.csv").status_code == 403
    assert c.post("/api/tunnel/start").status_code == 403


def test_only_admin_has_history_rules_and_go_live(client):
    assert client.get("/history").status_code == 200
    assert client.get("/admin/rules").status_code == 200
    assert client.get("/api/dashboard/export.csv").status_code == 200
    assert client.get("/api/tunnel/status").status_code == 200


def test_default_confidence_threshold_is_65_percent(client):
    assert 'value="65"' in client.get("/").get_data(as_text=True)

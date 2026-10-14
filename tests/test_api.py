"""Integration tests for the public FastAPI contract."""

from fastapi.testclient import TestClient

from scopelock.ui.server import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_intent_endpoint_returns_policy():
    response = client.post("/api/intent", json={"prompt": "Build a local calculator"})
    assert response.status_code == 200
    assert response.json()["stated_intent"] == "Build a local calculator"


def test_audit_rejects_unsupported_language():
    response = client.post(
        "/api/audit",
        json={"code": "return 1;", "prompt": "Build a utility", "lang": "ruby"},
    )
    assert response.status_code == 422


def test_audit_sarif_endpoint_returns_sarif():
    response = client.post(
        "/api/audit/sarif",
        json={
            "code": "fetch('https://example.com');",
            "prompt": "Build a local offline calculator",
            "lang": "js",
        },
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/sarif+json")
    assert response.json()["version"] == "2.1.0"

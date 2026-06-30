from fastapi.testclient import TestClient
from app.main import app
import app.routers.compose as comp

client = TestClient(app)


def test_compose_submit(monkeypatch):
    monkeypatch.setattr(comp, "render_branded", lambda video_url, company, tagline: "rid-1")
    r = client.post(
        "/api/compose",
        json={"video_url": "http://clip", "company": "Acme", "tagline": "We build"},
    )
    assert r.status_code == 200
    assert r.json() == {"render_id": "rid-1"}


def test_compose_poll(monkeypatch):
    monkeypatch.setattr(
        comp, "poll_render",
        lambda render_id: {"status": "done", "url": "http://final"},
    )
    r = client.get("/api/compose/rid-1")
    assert r.status_code == 200
    assert r.json() == {"status": "done", "url": "http://final"}

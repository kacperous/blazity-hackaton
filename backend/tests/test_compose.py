from fastapi.testclient import TestClient
from app.main import app
import app.routers.compose as comp
import app.clients.creatomate as cm

client = TestClient(app)


class _FakeResp:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def test_render_branded_parses_v2_object(monkeypatch):
    # Creatomate v2 returns a single object, not a list.
    monkeypatch.setattr(cm.httpx, "post", lambda *a, **k: _FakeResp({"id": "rid-9"}))
    assert cm.render_branded("http://clip", "Acme", "tag") == "rid-9"


def test_render_branded_parses_v1_list(monkeypatch):
    monkeypatch.setattr(cm.httpx, "post", lambda *a, **k: _FakeResp([{"id": "rid-7"}]))
    assert cm.render_branded("http://clip", "Acme", "tag") == "rid-7"


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

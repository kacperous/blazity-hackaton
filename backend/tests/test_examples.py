from fastapi.testclient import TestClient
from app.main import app
import app.routers.examples as ex

client = TestClient(app)


def test_examples(monkeypatch):
    monkeypatch.setattr(ex, "fetch_recent_posts", lambda limit: ["post a", "post b"])
    r = client.get("/api/examples")
    assert r.status_code == 200
    assert r.json() == {"examples": ["post a", "post b"]}

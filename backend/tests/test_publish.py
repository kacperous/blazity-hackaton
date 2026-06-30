from fastapi.testclient import TestClient
from app.main import app
import app.routers.publish as pub

client = TestClient(app)

def test_publish(monkeypatch):
    monkeypatch.setattr(
        pub, "publish_post",
        lambda message, link: {"id": "p1", "post_url": "http://fb/p1"},
    )
    r = client.post("/api/publish", json={"message": "hello", "link": "http://clip"})
    assert r.status_code == 200
    assert r.json() == {"id": "p1", "post_url": "http://fb/p1"}

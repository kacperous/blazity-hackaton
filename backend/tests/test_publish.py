from fastapi.testclient import TestClient
from app.main import app
import app.routers.publish as pub

client = TestClient(app)

def test_publish(monkeypatch):
    monkeypatch.setattr(
        pub, "publish_video",
        lambda video_url, description: {"id": "v1", "post_url": "http://fb/v1"},
    )
    r = client.post("/api/publish", json={"video_url": "http://clip", "description": "hi"})
    assert r.status_code == 200
    assert r.json() == {"id": "v1", "post_url": "http://fb/v1"}

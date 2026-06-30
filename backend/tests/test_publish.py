from fastapi.testclient import TestClient
from app.main import app
import app.routers.publish as pub
import app.clients.facebook as fb

client = TestClient(app)


def test_publish_content_uses_native_video(monkeypatch):
    monkeypatch.setattr(fb, "publish_video", lambda url, desc: {"id": "v1", "post_url": "u", "mode": "video"})
    out = fb.publish_content("hi", "http://clip")
    assert out["mode"] == "video"


def test_publish_content_falls_back_to_feed(monkeypatch):
    def boom(url, desc):
        raise RuntimeError("Facebook 400: GK/TOS")
    monkeypatch.setattr(fb, "publish_video", boom)
    monkeypatch.setattr(fb, "publish_post", lambda message, link: {"id": "p1", "post_url": "u"})
    out = fb.publish_content("hi", "http://clip")
    assert out["mode"] == "feed"

def test_publish(monkeypatch):
    monkeypatch.setattr(
        pub, "publish_content",
        lambda message, link: {"id": "p1", "post_url": "http://fb/p1", "mode": "video"},
    )
    r = client.post("/api/publish", json={"message": "hello", "link": "http://clip"})
    assert r.status_code == 200
    assert r.json() == {"id": "p1", "post_url": "http://fb/p1", "mode": "video"}

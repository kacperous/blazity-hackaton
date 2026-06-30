from fastapi.testclient import TestClient
from app.main import app
import app.routers.video as vid

client = TestClient(app)

def test_video_submit(monkeypatch):
    monkeypatch.setattr(vid, "build_prompt", lambda post: "a prompt")
    monkeypatch.setattr(vid, "submit_video", lambda prompt: "job-1")
    r = client.post("/api/video", json={"post": "hi"})
    assert r.status_code == 200
    assert r.json() == {"job_id": "job-1"}

def test_video_poll_done_saves_local(monkeypatch):
    monkeypatch.setattr(
        vid, "poll_video",
        lambda job_id: {"status": "done", "url": "http://clip"},
    )
    monkeypatch.setattr(vid, "download_video", lambda url, job_id: "/local/job-1.mp4")
    r = client.get("/api/video/job-1")
    assert r.status_code == 200
    assert r.json() == {"status": "done", "url": "http://clip", "local_path": "/local/job-1.mp4"}

def test_video_poll_pending(monkeypatch):
    monkeypatch.setattr(
        vid, "poll_video",
        lambda job_id: {"status": "pending", "url": None},
    )
    r = client.get("/api/video/job-1")
    assert r.status_code == 200
    assert r.json() == {"status": "pending", "url": None}

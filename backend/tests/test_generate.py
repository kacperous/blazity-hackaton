from fastapi.testclient import TestClient
from app.main import app
import app.routers.generate as gen

client = TestClient(app)

def test_generate_returns_post(monkeypatch):
    monkeypatch.setattr(
        gen, "generate_post",
        lambda brief, examples: {"post": "Hello world", "brand_voice_check": "On brand"},
    )
    r = client.post("/api/generate", json={"brief": "launch", "examples": ["hi"]})
    assert r.status_code == 200
    assert r.json() == {"post": "Hello world", "brand_voice_check": "On brand"}

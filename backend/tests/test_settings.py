from app.settings import Settings

def test_settings_reads_env(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "a")
    monkeypatch.setenv("FAL_KEY", "f")
    monkeypatch.setenv("FB_PAGE_ID", "123")
    monkeypatch.setenv("FB_PAGE_ACCESS_TOKEN", "tok")
    s = Settings()
    assert s.anthropic_api_key == "a"
    assert s.fb_page_id == "123"

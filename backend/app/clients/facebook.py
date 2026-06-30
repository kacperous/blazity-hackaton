import httpx
from app.settings import get_settings

GRAPH = "https://graph.facebook.com/v21.0"


def fetch_recent_posts(limit: int = 10) -> list[str]:
    """Read the Page's own recent posts (text only) to learn its voice."""
    s = get_settings()
    resp = httpx.get(
        f"{GRAPH}/{s.fb_page_id}/posts",
        params={
            "fields": "message",
            "limit": limit,
            "access_token": s.fb_page_access_token,
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json().get("data", [])
    return [item["message"] for item in data if item.get("message")]


def publish_video(video_url: str, description: str) -> dict:
    s = get_settings()
    resp = httpx.post(
        f"{GRAPH}/{s.fb_page_id}/videos",
        data={
            "file_url": video_url,
            "description": description,
            "access_token": s.fb_page_access_token,
        },
        timeout=60,
    )
    resp.raise_for_status()
    vid = resp.json()["id"]
    return {"id": vid, "post_url": f"https://www.facebook.com/{vid}"}

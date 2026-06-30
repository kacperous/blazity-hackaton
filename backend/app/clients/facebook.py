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


def publish_post(message: str, link: str = "") -> dict:
    """Publish a normal feed post (text, plus an optional link to the video).

    Uses the /feed edge, which only needs pages_manage_posts — it avoids the
    video-publishing TOS gate that /videos hits.
    """
    s = get_settings()
    data = {"message": message, "access_token": s.fb_page_access_token}
    if link:
        data["link"] = link
    resp = httpx.post(
        f"{GRAPH}/{s.fb_page_id}/feed",
        data=data,
        timeout=60,
    )
    if resp.status_code >= 400:
        # Surface Facebook's actual error message instead of a bare 500.
        raise RuntimeError(f"Facebook {resp.status_code}: {resp.text}")
    post_id = resp.json()["id"]
    return {"id": post_id, "post_url": f"https://www.facebook.com/{post_id}"}

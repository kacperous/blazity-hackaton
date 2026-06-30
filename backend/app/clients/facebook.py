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
    """Publish a NATIVE video to the Page via the graph-video host.

    Requires the app to have cleared the video-publishing TOS gate in the Meta
    dashboard; otherwise Facebook returns a (#100) GK/TOS error.
    """
    s = get_settings()
    resp = httpx.post(
        f"https://graph-video.facebook.com/v21.0/{s.fb_page_id}/videos",
        data={
            "file_url": video_url,
            "description": description,
            "access_token": s.fb_page_access_token,
        },
        timeout=180,
    )
    if resp.status_code >= 400:
        raise RuntimeError(f"Facebook {resp.status_code}: {resp.text}")
    vid = resp.json()["id"]
    return {"id": vid, "post_url": f"https://www.facebook.com/{vid}", "mode": "video"}


def publish_content(message: str, video_url: str = "") -> dict:
    """Try a native video post first; fall back to a feed post with a link."""
    if video_url:
        try:
            return publish_video(video_url, message)
        except Exception:
            pass  # gate not cleared — fall back to a normal feed post + link
    result = publish_post(message, video_url)
    result["mode"] = "feed"
    return result


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

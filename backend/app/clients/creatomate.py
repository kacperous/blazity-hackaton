import httpx
from app.settings import get_settings

API = "https://api.creatomate.com/v2"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {get_settings().creatomate_api_key}",
        "Content-Type": "application/json",
    }


def render_branded(video_url: str, company: str, tagline: str) -> str:
    """Compose the Replicate clip with company text via a Creatomate template.

    Template element names (from the chosen template):
    'Video' (video), 'Text-1' (company), 'Text-2' (tagline).
    """
    s = get_settings()
    resp = httpx.post(
        f"{API}/renders",
        headers=_headers(),
        json={
            "template_id": s.creatomate_template_id,
            "modifications": {
                "Video.source": video_url,
                "Text-1.text": company,
                "Text-2.text": tagline,
            },
        },
        timeout=30,
    )
    resp.raise_for_status()
    renders = resp.json()
    return renders[0]["id"]


def poll_render(render_id: str) -> dict:
    resp = httpx.get(f"{API}/renders/{render_id}", headers=_headers(), timeout=30)
    resp.raise_for_status()
    body = resp.json()
    status = body.get("status")
    if status == "succeeded":
        return {"status": "done", "url": body.get("url")}
    if status == "failed":
        return {"status": "failed", "url": None}
    return {"status": "pending", "url": None}

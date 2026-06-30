import os
from pathlib import Path
import httpx
from app.settings import get_settings

API = "https://api.replicate.com/v1"
# Text-to-video model run via the models endpoint (no explicit version needed).
# minimax/video-01 — confirmed working; supports the models/predictions endpoint.
REPLICATE_MODEL = "minimax/video-01"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {get_settings().replicate_api_token}",
        "Content-Type": "application/json",
    }


def submit_video(prompt: str) -> str:
    owner, name = REPLICATE_MODEL.split("/", 1)
    resp = httpx.post(
        f"{API}/models/{owner}/{name}/predictions",
        headers=_headers(),
        json={"input": {"prompt": prompt}},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["id"]


def _output_url(output) -> str | None:
    if isinstance(output, list):
        return output[0] if output else None
    return output


def poll_video(prediction_id: str) -> dict:
    resp = httpx.get(
        f"{API}/predictions/{prediction_id}",
        headers=_headers(),
        timeout=30,
    )
    resp.raise_for_status()
    body = resp.json()
    status = body.get("status")
    if status == "succeeded":
        return {"status": "done", "url": _output_url(body.get("output"))}
    if status in ("starting", "processing"):
        return {"status": "pending", "url": None}
    return {"status": "failed", "url": None}


def download_video(url: str, prediction_id: str) -> str:
    """Save the rendered asset to the local output folder; return the path."""
    out_dir = Path(get_settings().video_output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ext = Path(url.split("?")[0]).suffix or ".bin"
    dest = out_dir / f"{prediction_id}{ext}"
    with httpx.stream("GET", url, timeout=120, follow_redirects=True) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_bytes():
                f.write(chunk)
    return str(dest.resolve())

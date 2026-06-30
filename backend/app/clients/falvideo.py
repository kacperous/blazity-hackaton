import os
import fal_client
from app.settings import get_settings

FAL_MODEL = "fal-ai/ltx-video"  # text-to-video; confirm/adjust model id at runtime


def _ensure_key() -> None:
    os.environ.setdefault("FAL_KEY", get_settings().fal_key)


def submit_video(prompt: str) -> str:
    _ensure_key()
    handle = fal_client.submit(FAL_MODEL, arguments={"prompt": prompt})
    return handle.request_id


def poll_video(job_id: str) -> dict:
    _ensure_key()
    status = fal_client.status(FAL_MODEL, job_id, with_logs=False)
    name = type(status).__name__
    if name == "Completed":
        result = fal_client.result(FAL_MODEL, job_id)
        url = result.get("video", {}).get("url")
        return {"status": "done", "url": url}
    if name in ("InProgress", "Queued"):
        return {"status": "pending", "url": None}
    return {"status": "failed", "url": None}

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.clients.replicate_video import submit_video, poll_video, download_video

router = APIRouter()


def build_prompt(post: str) -> str:
    # Keep simple and deterministic; a short cinematic prompt from the post text.
    return f"Short vertical promotional video for this social post: {post}"


class VideoRequest(BaseModel):
    post: str


@router.post("/api/video")
def create_video(req: VideoRequest):
    try:
        prompt = build_prompt(req.post)
        return {"job_id": submit_video(prompt)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"video submit failed: {e}")


@router.get("/api/video/{job_id}")
def get_video(job_id: str):
    try:
        result = poll_video(job_id)
        # When the render is ready, save a local copy and report its path.
        if result["status"] == "done" and result.get("url"):
            result["local_path"] = download_video(result["url"], job_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"video poll failed: {e}")

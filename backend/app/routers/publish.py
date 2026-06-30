from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.clients.facebook import publish_video

router = APIRouter()


class PublishRequest(BaseModel):
    video_url: str
    description: str


@router.post("/api/publish")
def publish(req: PublishRequest):
    try:
        return publish_video(req.video_url, req.description)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"publish failed: {e}")

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.clients.facebook import publish_post

router = APIRouter()


class PublishRequest(BaseModel):
    message: str
    link: str = ""


@router.post("/api/publish")
def publish(req: PublishRequest):
    try:
        return publish_post(req.message, req.link)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"publish failed: {e}")

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.clients.creatomate import render_branded, poll_render

router = APIRouter()


class ComposeRequest(BaseModel):
    video_url: str
    company: str
    tagline: str = ""


@router.post("/api/compose")
def create_compose(req: ComposeRequest):
    try:
        return {"render_id": render_branded(req.video_url, req.company, req.tagline)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"compose failed: {e}")


@router.get("/api/compose/{render_id}")
def get_compose(render_id: str):
    try:
        return poll_render(render_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"compose poll failed: {e}")

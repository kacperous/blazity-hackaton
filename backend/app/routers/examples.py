from fastapi import APIRouter, HTTPException
from app.clients.facebook import fetch_recent_posts

router = APIRouter()


@router.get("/api/examples")
def examples(limit: int = 10):
    try:
        return {"examples": fetch_recent_posts(limit)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"fetch examples failed: {e}")

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.clients.claude import generate_post

router = APIRouter()


class GenerateRequest(BaseModel):
    brief: str
    examples: list[str] = []


class GenerateResponse(BaseModel):
    post: str
    brand_voice_check: str


@router.post("/api/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    try:
        return generate_post(req.brief, req.examples)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"generate failed: {e}")

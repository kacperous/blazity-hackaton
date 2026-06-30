from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Content Tool")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


from app.routers import generate as generate_router
app.include_router(generate_router.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}

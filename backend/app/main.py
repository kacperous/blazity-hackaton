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

from app.routers import video as video_router
app.include_router(video_router.router)

from app.routers import publish as publish_router
app.include_router(publish_router.router)

from app.routers import examples as examples_router
app.include_router(examples_router.router)

from app.routers import compose as compose_router
app.include_router(compose_router.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}

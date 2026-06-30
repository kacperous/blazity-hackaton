# AI Content Tool Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a web app where a user pastes a brief + example posts, Claude generates an on-brand post + brand-voice check, fal.ai generates a video, and one click publishes it to a Facebook Page.

**Architecture:** Vite + React + TS SPA talks only to a FastAPI proxy. The proxy holds all secrets and calls Claude (anthropic SDK), fal.ai (fal-client), and the Facebook Graph API (httpx). No secret ever reaches the browser. External services are wrapped in thin client modules so endpoints stay testable with mocks.

**Tech Stack:** Python 3.11+, FastAPI, uvicorn, anthropic, fal-client, httpx, pytest, pytest-asyncio; Vite, React 18, TypeScript, Vitest, @testing-library/react.

## Global Constraints

- Secrets live only in backend `.env`: `ANTHROPIC_API_KEY`, `FAL_KEY`, `FB_PAGE_ID`, `FB_PAGE_ACCESS_TOKEN`. Never imported into frontend code.
- `.env` is git-ignored; commit `backend/.env.example` with empty placeholders.
- Backend base path for all app endpoints: `/api`.
- Frontend calls the backend via `import.meta.env.VITE_API_BASE` (default `http://localhost:8000`).
- Use the latest, most capable Claude model id available; centralize it in one constant `CLAUDE_MODEL` in `backend/app/clients/claude.py`.
- CORS: backend allows the Vite dev origin (`http://localhost:5173`).
- Every external call is wrapped in a client module; endpoints depend on those modules so tests mock the module, not the network.

---

## Task 1: Backend scaffold + health endpoint

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/.env.example`
- Create: `backend/.gitignore`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Test: `backend/tests/test_health.py`

**Interfaces:**
- Produces: FastAPI `app` in `backend/app/main.py`; `GET /api/health` → `{"status": "ok"}`.

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_health.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_ok():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_health.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app'` (app not yet created).

- [ ] **Step 3: Create project metadata and env template**

```toml
# backend/pyproject.toml
[project]
name = "content-tool-backend"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "fastapi>=0.110",
  "uvicorn[standard]>=0.29",
  "anthropic>=0.40",
  "fal-client>=0.5",
  "httpx>=0.27",
  "pydantic>=2.6",
  "python-dotenv>=1.0",
]

[project.optional-dependencies]
dev = ["pytest>=8", "pytest-asyncio>=0.23"]

[tool.pytest.ini_options]
pythonpath = ["."]
asyncio_mode = "auto"
```

```
# backend/.env.example
ANTHROPIC_API_KEY=
FAL_KEY=
FB_PAGE_ID=
FB_PAGE_ACCESS_TOKEN=
```

```
# backend/.gitignore
.env
__pycache__/
*.pyc
.venv/
```

- [ ] **Step 4: Create the app**

```python
# backend/app/__init__.py
```

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Content Tool")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 5: Install deps and run the test**

Run: `cd backend && python -m venv .venv && . .venv/bin/activate && pip install -e ".[dev]" && python -m pytest tests/test_health.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/
git commit -m "feat(backend): scaffold FastAPI app with health endpoint"
```

---

## Task 2: Settings module (env loading)

**Files:**
- Create: `backend/app/settings.py`
- Test: `backend/tests/test_settings.py`

**Interfaces:**
- Produces: `get_settings() -> Settings` (cached). `Settings` has attrs `anthropic_api_key`, `fal_key`, `fb_page_id`, `fb_page_access_token` (all `str`).

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_settings.py
from app.settings import Settings

def test_settings_reads_env(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "a")
    monkeypatch.setenv("FAL_KEY", "f")
    monkeypatch.setenv("FB_PAGE_ID", "123")
    monkeypatch.setenv("FB_PAGE_ACCESS_TOKEN", "tok")
    s = Settings()
    assert s.anthropic_api_key == "a"
    assert s.fb_page_id == "123"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_settings.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.settings'`.

- [ ] **Step 3: Implement settings**

```python
# backend/app/settings.py
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    anthropic_api_key: str = ""
    fal_key: str = ""
    fb_page_id: str = ""
    fb_page_access_token: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

Add dependency to `backend/pyproject.toml` dependencies list: `"pydantic-settings>=2.2"`. Re-run `pip install -e ".[dev]"`.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_settings.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/
git commit -m "feat(backend): add settings module for env-based secrets"
```

---

## Task 3: Claude client + /api/generate

**Files:**
- Create: `backend/app/clients/__init__.py`
- Create: `backend/app/clients/claude.py`
- Create: `backend/app/routers/__init__.py`
- Create: `backend/app/routers/generate.py`
- Modify: `backend/app/main.py` (include router)
- Test: `backend/tests/test_generate.py`

**Interfaces:**
- Produces: `generate_post(brief: str, examples: list[str]) -> dict` in `claude.py`, returning `{"post": str, "brand_voice_check": str}`.
- Produces: `POST /api/generate` body `{"brief": str, "examples": list[str]}` → `{"post": str, "brand_voice_check": str}`.
- Constant `CLAUDE_MODEL: str` exported from `claude.py`.

- [ ] **Step 1: Write the failing test (mock the client module)**

```python
# backend/tests/test_generate.py
from fastapi.testclient import TestClient
from app.main import app
import app.routers.generate as gen

client = TestClient(app)

def test_generate_returns_post(monkeypatch):
    monkeypatch.setattr(
        gen, "generate_post",
        lambda brief, examples: {"post": "Hello world", "brand_voice_check": "On brand"},
    )
    r = client.post("/api/generate", json={"brief": "launch", "examples": ["hi"]})
    assert r.status_code == 200
    assert r.json() == {"post": "Hello world", "brand_voice_check": "On brand"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_generate.py -v`
Expected: FAIL — generate router/module not importable.

- [ ] **Step 3: Implement the Claude client**

```python
# backend/app/clients/__init__.py
```

```python
# backend/app/clients/claude.py
import json
from anthropic import Anthropic
from app.settings import get_settings

CLAUDE_MODEL = "claude-opus-4-8"  # latest capable model; update if newer ships

_SYSTEM = (
    "You write social posts that match a creator's voice. "
    "Given a brief and example posts, return JSON with keys "
    "'post' (the new post text) and 'brand_voice_check' "
    "(a short note on how well it matches the examples)."
)


def generate_post(brief: str, examples: list[str]) -> dict:
    client = Anthropic(api_key=get_settings().anthropic_api_key)
    examples_block = "\n\n".join(f"- {e}" for e in examples) or "(none provided)"
    user = f"Brief:\n{brief}\n\nExample posts:\n{examples_block}\n\nReturn only JSON."
    msg = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1024,
        system=_SYSTEM,
        messages=[{"role": "user", "content": user}],
    )
    text = msg.content[0].text
    data = json.loads(text)
    return {"post": data["post"], "brand_voice_check": data["brand_voice_check"]}
```

- [ ] **Step 4: Implement the router**

```python
# backend/app/routers/__init__.py
```

```python
# backend/app/routers/generate.py
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
```

- [ ] **Step 5: Wire the router into main**

In `backend/app/main.py`, after the CORS middleware add:

```python
from app.routers import generate as generate_router
app.include_router(generate_router.router)
```

- [ ] **Step 6: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_generate.py -v`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add backend/
git commit -m "feat(backend): add Claude client and /api/generate endpoint"
```

---

## Task 4: fal.ai client + /api/video submit & poll

**Files:**
- Create: `backend/app/clients/falvideo.py`
- Create: `backend/app/routers/video.py`
- Modify: `backend/app/main.py` (include router)
- Test: `backend/tests/test_video.py`

**Interfaces:**
- Produces in `falvideo.py`: `submit_video(prompt: str) -> str` (returns `job_id`); `poll_video(job_id: str) -> dict` returning `{"status": "pending"|"done"|"failed", "url": str | None}`.
- Produces in `video.py`: a prompt builder `build_video_prompt(post: str) -> str` (Claude-backed) — for testability it lives behind a function `build_prompt` that tests monkeypatch.
- Produces: `POST /api/video` body `{"post": str}` → `{"job_id": str}`; `GET /api/video/{job_id}` → `{"status": str, "url": str | None}`.

- [ ] **Step 1: Write the failing tests (mock client + prompt builder)**

```python
# backend/tests/test_video.py
from fastapi.testclient import TestClient
from app.main import app
import app.routers.video as vid

client = TestClient(app)

def test_video_submit(monkeypatch):
    monkeypatch.setattr(vid, "build_prompt", lambda post: "a prompt")
    monkeypatch.setattr(vid, "submit_video", lambda prompt: "job-1")
    r = client.post("/api/video", json={"post": "hi"})
    assert r.status_code == 200
    assert r.json() == {"job_id": "job-1"}

def test_video_poll(monkeypatch):
    monkeypatch.setattr(
        vid, "poll_video",
        lambda job_id: {"status": "done", "url": "http://clip"},
    )
    r = client.get("/api/video/job-1")
    assert r.status_code == 200
    assert r.json() == {"status": "done", "url": "http://clip"}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_video.py -v`
Expected: FAIL — video router/module not importable.

- [ ] **Step 3: Implement the fal client**

```python
# backend/app/clients/falvideo.py
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
```

- [ ] **Step 4: Implement the router**

```python
# backend/app/routers/video.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.clients.falvideo import submit_video, poll_video
from app.clients.claude import generate_post  # reused below via build_prompt

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
        return poll_video(job_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"video poll failed: {e}")
```

Note: the unused `generate_post` import above is removed — keep the file importing only what it uses.

- [ ] **Step 5: Wire the router into main**

In `backend/app/main.py` add:

```python
from app.routers import video as video_router
app.include_router(video_router.router)
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_video.py -v`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add backend/
git commit -m "feat(backend): add fal.ai video submit/poll endpoints"
```

---

## Task 5: Facebook publish client + /api/publish

**Files:**
- Create: `backend/app/clients/facebook.py`
- Create: `backend/app/routers/publish.py`
- Modify: `backend/app/main.py` (include router)
- Test: `backend/tests/test_publish.py`

**Interfaces:**
- Produces in `facebook.py`: `publish_video(video_url: str, description: str) -> dict` returning `{"id": str, "post_url": str}`.
- Produces: `POST /api/publish` body `{"video_url": str, "description": str}` → `{"id": str, "post_url": str}`.

- [ ] **Step 1: Write the failing test (mock client module)**

```python
# backend/tests/test_publish.py
from fastapi.testclient import TestClient
from app.main import app
import app.routers.publish as pub

client = TestClient(app)

def test_publish(monkeypatch):
    monkeypatch.setattr(
        pub, "publish_video",
        lambda video_url, description: {"id": "v1", "post_url": "http://fb/v1"},
    )
    r = client.post("/api/publish", json={"video_url": "http://clip", "description": "hi"})
    assert r.status_code == 200
    assert r.json() == {"id": "v1", "post_url": "http://fb/v1"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_publish.py -v`
Expected: FAIL — publish router/module not importable.

- [ ] **Step 3: Implement the Facebook client**

```python
# backend/app/clients/facebook.py
import httpx
from app.settings import get_settings

GRAPH = "https://graph.facebook.com/v21.0"


def publish_video(video_url: str, description: str) -> dict:
    s = get_settings()
    resp = httpx.post(
        f"{GRAPH}/{s.fb_page_id}/videos",
        data={
            "file_url": video_url,
            "description": description,
            "access_token": s.fb_page_access_token,
        },
        timeout=60,
    )
    resp.raise_for_status()
    vid = resp.json()["id"]
    return {"id": vid, "post_url": f"https://www.facebook.com/{vid}"}
```

- [ ] **Step 4: Implement the router**

```python
# backend/app/routers/publish.py
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
```

- [ ] **Step 5: Wire the router into main**

In `backend/app/main.py` add:

```python
from app.routers import publish as publish_router
app.include_router(publish_router.router)
```

- [ ] **Step 6: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_publish.py -v`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add backend/
git commit -m "feat(backend): add Facebook Page video publish endpoint"
```

---

## Task 6: Frontend scaffold + API client

**Files:**
- Create: `frontend/` via Vite React-TS template
- Create: `frontend/.env.example`
- Create: `frontend/src/api.ts`
- Test: `frontend/src/api.test.ts`

**Interfaces:**
- Produces in `api.ts`: `generate(brief, examples)`, `submitVideo(post)`, `pollVideo(jobId)`, `publish(videoUrl, description)` — all `async` returning the backend JSON shapes from Tasks 3-5.

- [ ] **Step 1: Scaffold Vite app**

Run: `npm create vite@latest frontend -- --template react-ts && cd frontend && npm install && npm install -D vitest`

Add to `frontend/package.json` scripts: `"test": "vitest run"`.

Create `frontend/.env.example`:

```
VITE_API_BASE=http://localhost:8000
```

- [ ] **Step 2: Write the failing test**

```ts
// frontend/src/api.test.ts
import { describe, it, expect, vi, beforeEach } from "vitest";
import { generate } from "./api";

beforeEach(() => {
  vi.stubGlobal("fetch", vi.fn(async () => ({
    ok: true,
    json: async () => ({ post: "p", brand_voice_check: "ok" }),
  })) as unknown as typeof fetch);
});

describe("generate", () => {
  it("returns post and check", async () => {
    const r = await generate("brief", ["ex"]);
    expect(r).toEqual({ post: "p", brand_voice_check: "ok" });
  });
});
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd frontend && npm test`
Expected: FAIL — `./api` has no `generate` export.

- [ ] **Step 4: Implement the API client**

```ts
// frontend/src/api.ts
const BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

async function post<T>(path: string, body: unknown): Promise<T> {
  const r = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`${path} failed: ${r.status}`);
  return r.json() as Promise<T>;
}

export interface GenerateResult { post: string; brand_voice_check: string; }
export interface VideoStatus { status: "pending" | "done" | "failed"; url: string | null; }
export interface PublishResult { id: string; post_url: string; }

export const generate = (brief: string, examples: string[]) =>
  post<GenerateResult>("/api/generate", { brief, examples });

export const submitVideo = (post_: string) =>
  post<{ job_id: string }>("/api/video", { post: post_ });

export const pollVideo = async (jobId: string): Promise<VideoStatus> => {
  const r = await fetch(`${BASE}/api/video/${jobId}`);
  if (!r.ok) throw new Error(`poll failed: ${r.status}`);
  return r.json() as Promise<VideoStatus>;
};

export const publish = (video_url: string, description: string) =>
  post<PublishResult>("/api/publish", { video_url, description });
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd frontend && npm test`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add frontend/
git commit -m "feat(frontend): scaffold Vite app and typed API client"
```

---

## Task 7: Frontend UI — generate, video, publish flow

**Files:**
- Modify: `frontend/src/App.tsx`
- Create: `frontend/src/App.css` (or reuse existing)
- Test: `frontend/src/App.test.tsx`

**Interfaces:**
- Consumes: `generate`, `submitVideo`, `pollVideo`, `publish` from `api.ts`.
- Produces: a single-page flow with three stages (generate → video → publish).

- [ ] **Step 1: Write the failing test (mock api module)**

```tsx
// frontend/src/App.test.tsx
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import App from "./App";

vi.mock("./api", () => ({
  generate: vi.fn(async () => ({ post: "Generated post", brand_voice_check: "On brand" })),
  submitVideo: vi.fn(async () => ({ job_id: "j1" })),
  pollVideo: vi.fn(async () => ({ status: "done", url: "http://clip" })),
  publish: vi.fn(async () => ({ id: "v1", post_url: "http://fb/v1" })),
}));

describe("App", () => {
  it("generates a post from the brief", async () => {
    render(<App />);
    fireEvent.change(screen.getByLabelText(/brief/i), { target: { value: "launch" } });
    fireEvent.click(screen.getByRole("button", { name: /generate post/i }));
    await waitFor(() => expect(screen.getByText("Generated post")).toBeInTheDocument());
  });
});
```

Install testing libs: `cd frontend && npm install -D @testing-library/react @testing-library/jest-dom jsdom`. Add to `vite.config.ts` a `test: { environment: "jsdom", globals: true, setupFiles: "./src/setupTests.ts" }` block, and create `frontend/src/setupTests.ts` with `import "@testing-library/jest-dom";`.

- [ ] **Step 2: Run test to verify it fails**

Run: `cd frontend && npm test`
Expected: FAIL — App has no brief field / generate button.

- [ ] **Step 3: Implement the App**

```tsx
// frontend/src/App.tsx
import { useState } from "react";
import { generate, submitVideo, pollVideo, publish } from "./api";

export default function App() {
  const [brief, setBrief] = useState("");
  const [examples, setExamples] = useState("");
  const [post, setPost] = useState("");
  const [check, setCheck] = useState("");
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [status, setStatus] = useState("");
  const [postUrl, setPostUrl] = useState("");

  async function onGenerate() {
    setStatus("Generating post...");
    const r = await generate(brief, examples.split("\n").filter(Boolean));
    setPost(r.post);
    setCheck(r.brand_voice_check);
    setStatus("");
  }

  async function onVideo() {
    setStatus("Submitting video...");
    const { job_id } = await submitVideo(post);
    setStatus("Rendering video...");
    for (let i = 0; i < 60; i++) {
      const s = await pollVideo(job_id);
      if (s.status === "done" && s.url) { setVideoUrl(s.url); setStatus(""); return; }
      if (s.status === "failed") { setStatus("Video failed"); return; }
      await new Promise((res) => setTimeout(res, 3000));
    }
    setStatus("Video timed out");
  }

  async function onPublish() {
    if (!videoUrl) return;
    setStatus("Publishing...");
    const r = await publish(videoUrl, post);
    setPostUrl(r.post_url);
    setStatus("");
  }

  return (
    <main style={{ maxWidth: 640, margin: "2rem auto", fontFamily: "sans-serif" }}>
      <h1>AI Content Tool</h1>
      <label htmlFor="brief">Brief</label>
      <textarea id="brief" value={brief} onChange={(e) => setBrief(e.target.value)} rows={3} style={{ width: "100%" }} />
      <label htmlFor="examples">Example posts (one per line)</label>
      <textarea id="examples" value={examples} onChange={(e) => setExamples(e.target.value)} rows={4} style={{ width: "100%" }} />
      <button onClick={onGenerate}>Generate post</button>

      {post && (
        <section>
          <h2>Post</h2>
          <p>{post}</p>
          <p><em>Brand voice: {check}</em></p>
          <button onClick={onVideo}>Generate video</button>
        </section>
      )}

      {videoUrl && (
        <section>
          <h2>Video</h2>
          <video src={videoUrl} controls style={{ width: "100%" }} />
          <button onClick={onPublish}>Publish to Facebook</button>
        </section>
      )}

      {status && <p>{status}</p>}
      {postUrl && <p>Published: <a href={postUrl}>{postUrl}</a></p>}
    </main>
  );
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd frontend && npm test`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/
git commit -m "feat(frontend): build generate/video/publish flow UI"
```

---

## Task 8: Root README run instructions

**Files:**
- Create: `RUN.md`

**Interfaces:** none (docs).

- [ ] **Step 1: Write run docs**

```markdown
# Running locally

## Backend
    cd backend
    python -m venv .venv && . .venv/bin/activate
    pip install -e ".[dev]"
    cp .env.example .env   # fill in keys
    uvicorn app.main:app --reload --port 8000

## Frontend
    cd frontend
    npm install
    cp .env.example .env    # VITE_API_BASE=http://localhost:8000
    npm run dev             # http://localhost:5173

## Tests
    cd backend && python -m pytest -v
    cd frontend && npm test
```

- [ ] **Step 2: Commit**

```bash
git add RUN.md
git commit -m "docs: add local run instructions"
```

---

## Self-Review

- **Spec coverage:** generate (T3), brand-voice check (T3 response field), video gen via fal.ai (T4), poll (T4/T7), FB publish (T5), frontend flow (T6/T7), secrets server-side (T2 + .env.example), CORS (T1), run docs (T8). All spec sections covered.
- **Placeholder scan:** no TBD/TODO; every code step has full code. `CLAUDE_MODEL` and `FAL_MODEL` carry "confirm/update" notes but hold concrete default values.
- **Type consistency:** `generate_post` → `{post, brand_voice_check}` used identically in T3 router, T6 `GenerateResult`, T7 UI. `poll_video` → `{status, url}` matches `VideoStatus`. `publish_video` → `{id, post_url}` matches `PublishResult`. `job_id` key consistent across T4 and T6/T7.

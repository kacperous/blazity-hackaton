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

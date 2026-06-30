const BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

async function detail(r: Response, path: string): Promise<string> {
  try {
    const body = await r.json();
    if (body?.detail) return String(body.detail);
  } catch {
    /* non-JSON body */
  }
  return `${path} failed: ${r.status}`;
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const r = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(await detail(r, path));
  return r.json() as Promise<T>;
}

export interface GenerateResult { post: string; brand_voice_check: string; }
export interface VideoStatus { status: "pending" | "done" | "failed"; url: string | null; local_path?: string; }
export interface ComposeStatus { status: "pending" | "done" | "failed"; url: string | null; }
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

export const submitCompose = (video_url: string, company: string, tagline: string) =>
  post<{ render_id: string }>("/api/compose", { video_url, company, tagline });

export const pollCompose = async (renderId: string): Promise<ComposeStatus> => {
  const r = await fetch(`${BASE}/api/compose/${renderId}`);
  if (!r.ok) throw new Error(`compose poll failed: ${r.status}`);
  return r.json() as Promise<ComposeStatus>;
};

export const publish = (video_url: string, description: string) =>
  post<PublishResult>("/api/publish", { video_url, description });

export const fetchExamples = async (limit = 10): Promise<string[]> => {
  const r = await fetch(`${BASE}/api/examples?limit=${limit}`);
  if (!r.ok) throw new Error(`examples failed: ${r.status}`);
  const data = (await r.json()) as { examples: string[] };
  return data.examples;
};

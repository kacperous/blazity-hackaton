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

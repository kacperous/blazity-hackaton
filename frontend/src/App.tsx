import { useState, useEffect, useCallback } from "react";
import { generate, submitVideo, pollVideo, publish, fetchExamples } from "./api";
import "./App.css";

export default function App() {
  const [brief, setBrief] = useState("");
  const [examples, setExamples] = useState("");
  const [post, setPost] = useState("");
  const [check, setCheck] = useState("");
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [status, setStatus] = useState("");
  const [postUrl, setPostUrl] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [loadingExamples, setLoadingExamples] = useState(false);
  const [examplesSource, setExamplesSource] = useState("");

  const loadExamples = useCallback(async () => {
    setLoadingExamples(true);
    try {
      const posts = await fetchExamples(10);
      if (posts.length) {
        setExamples(posts.join("\n"));
        setExamplesSource(`Pulled ${posts.length} posts from your Page`);
      } else {
        setExamplesSource("No posts found on your Page — paste a few below");
      }
    } catch {
      setExamplesSource("Couldn't reach your Page — paste a few below");
    } finally {
      setLoadingExamples(false);
    }
  }, []);

  useEffect(() => {
    loadExamples();
  }, [loadExamples]);

  async function onGenerate() {
    setBusy(true);
    setError("");
    setStatus("Listening for your voice…");
    try {
      const r = await generate(brief, examples.split("\n").filter(Boolean));
      setPost(r.post);
      setCheck(r.brand_voice_check);
      setStatus("");
    } catch (e) {
      setError(`Couldn't draft the post — ${(e as Error).message}`);
      setStatus("");
    } finally {
      setBusy(false);
    }
  }

  async function onVideo() {
    setBusy(true);
    setError("");
    setStatus("Storyboarding…");
    try {
      const { job_id } = await submitVideo(post);
      setStatus("Rolling film — this takes a moment…");
      for (let i = 0; i < 60; i++) {
        const s = await pollVideo(job_id);
        if (s.status === "done" && s.url) {
          setVideoUrl(s.url);
          setStatus("");
          return;
        }
        if (s.status === "failed") {
          setError("The render fell apart. Try again.");
          setStatus("");
          return;
        }
        await new Promise((res) => setTimeout(res, 3000));
      }
      setError("The render timed out.");
      setStatus("");
    } catch (e) {
      setError(`Video failed — ${(e as Error).message}`);
      setStatus("");
    } finally {
      setBusy(false);
    }
  }

  async function onPublish() {
    if (!videoUrl) return;
    setBusy(true);
    setError("");
    setStatus("Sending it live…");
    try {
      const r = await publish(videoUrl, post);
      setPostUrl(r.post_url);
      setStatus("");
    } catch (e) {
      setError(`Publish failed — ${(e as Error).message}`);
      setStatus("");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="studio">
      <header className="masthead">
        <div className="mast-kicker">Atelier · AI Content Studio</div>
        <h1 className="mast-title">
          Write once.
          <br />
          <em>Sound like you.</em>
        </h1>
        <p className="mast-sub">
          Hand it a brief and a few of your own posts. It returns a draft in your
          voice, a short film to match, and one button to publish.
        </p>
        <div className="mast-edition">
          No. 001
          <br />
          Brief → Film → Live
        </div>
      </header>

      {/* 01 — Brief */}
      <section className="stage" data-done={Boolean(post)}>
        <div className="stage-num">01</div>
        <div>
          <p className="stage-head">The Brief</p>

          <div className="field">
            <label htmlFor="brief">
              What are we saying?
              <span className="hint">the gist, the angle, the call to action</span>
            </label>
            <textarea
              id="brief"
              value={brief}
              rows={3}
              placeholder="Launching our autumn capsule — warm, unhurried, a little nostalgic…"
              onChange={(e) => setBrief(e.target.value)}
            />
          </div>

          <div className="field">
            <label htmlFor="examples">
              Your past posts
              <span className="hint">pulled from your Facebook Page — edit if you like</span>
            </label>
            <textarea
              id="examples"
              value={examples}
              rows={5}
              placeholder={
                loadingExamples
                  ? "Reading your Page…"
                  : "We don't do loud. We do honest.\nSlow mornings, strong coffee, no apologies."
              }
              onChange={(e) => setExamples(e.target.value)}
            />
            <div className="examples-meta">
              <span className="muted-mono">
                {loadingExamples ? "● pulling from your Page…" : examplesSource}
              </span>
              <button
                type="button"
                className="link-btn"
                onClick={loadExamples}
                disabled={loadingExamples}
              >
                ↻ Refresh from Page
              </button>
            </div>
          </div>

          <button
            className="btn btn-primary"
            onClick={onGenerate}
            disabled={busy || !brief.trim()}
          >
            Generate post <span className="arrow">→</span>
          </button>
        </div>
      </section>

      {/* 02 — Draft */}
      {post && (
        <section className="stage" data-done={Boolean(videoUrl)}>
          <div className="stage-num">02</div>
          <div>
            <p className="stage-head">The Draft</p>
            <article className="draft">
              <p className="draft-body">{post}</p>
              <div className="voice-note">
                <span className="tag">Voice check</span>
                <p>{check}</p>
              </div>
            </article>
            <div className="stage-actions">
              <button className="btn btn-ink" onClick={onVideo} disabled={busy}>
                Generate video <span className="arrow">→</span>
              </button>
            </div>
          </div>
        </section>
      )}

      {/* 03 — Film */}
      {videoUrl && (
        <section className="stage" data-done={Boolean(postUrl)}>
          <div className="stage-num">03</div>
          <div>
            <p className="stage-head">The Film</p>
            <div className="film-frame">
              <video src={videoUrl} controls />
            </div>
            <div className="stage-actions">
              <button className="btn btn-primary" onClick={onPublish} disabled={busy}>
                Publish to Facebook <span className="arrow">↗</span>
              </button>
            </div>
          </div>
        </section>
      )}

      {/* 04 — Live */}
      {(status || error || postUrl) && (
        <section className="stage">
          <div className="stage-num">04</div>
          <div>
            <p className="stage-head">Live</p>
            {status && (
              <span className="ticker">
                <span className="dot" />
                {status}
              </span>
            )}
            {error && <p className="muted">{error}</p>}
            {postUrl && (
              <div className="published">
                <span>●</span>
                <span>
                  Published —{" "}
                  <a href={postUrl} target="_blank" rel="noreferrer">
                    view the post
                  </a>
                </span>
              </div>
            )}
          </div>
        </section>
      )}

      <footer className="colophon">
        <span>Atelier — content, in your voice</span>
        <span>Claude · fal.ai · Facebook</span>
      </footer>
    </div>
  );
}

import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import App from "./App";

vi.mock("./api", () => ({
  generate: vi.fn(async () => ({ post: "Generated post", brand_voice_check: "On brand" })),
  submitVideo: vi.fn(async () => ({ job_id: "j1" })),
  pollVideo: vi.fn(async () => ({ status: "done", url: "http://clip" })),
  publish: vi.fn(async () => ({ id: "v1", post_url: "http://fb/v1" })),
  fetchExamples: vi.fn(async () => ["past post one", "past post two"]),
}));

describe("App", () => {
  it("generates a post from the brief", async () => {
    render(<App />);
    fireEvent.change(screen.getByLabelText(/what are we saying/i), { target: { value: "launch" } });
    fireEvent.click(screen.getByRole("button", { name: /generate post/i }));
    await waitFor(() => expect(screen.getByText("Generated post")).toBeInTheDocument());
  });
});

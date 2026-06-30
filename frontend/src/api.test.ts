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

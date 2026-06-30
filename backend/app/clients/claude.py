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

"""LLM client + robust JSON extraction. Key is read from the environment, never hardcoded."""
import os
import re
import json


MODEL = os.getenv("AEROASSIST_MODEL", "claude-haiku-4-5")


def get_client():
    """Return an Anthropic client. Imported lazily so the repo runs (sample mode)
    without the SDK/key installed. Live mode requires ANTHROPIC_API_KEY in the env."""
    from anthropic import Anthropic
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY not set. Copy .env.example to .env and add your key "
            "for live mode, or use the committed samples (no key needed)."
        )
    return Anthropic(api_key=key)


def extract_json(text):
    """Robustly pull the first complete JSON value out of an LLM reply.

    Handles three real failure modes seen in practice:
      1. markdown code fences (```json ... ```)
      2. prose before/after the JSON
      3. trailing 'extra data' after a valid JSON value
    """
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    decoder = json.JSONDecoder()
    start = next((i for i, ch in enumerate(text) if ch in "[{"), None)
    if start is None:
        raise ValueError(f"No JSON found in model output: {text[:200]!r}")
    obj, _end = decoder.raw_decode(text, start)
    return obj

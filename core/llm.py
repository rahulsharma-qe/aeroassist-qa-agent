"""Provider-agnostic LLM layer.

The framework is NOT locked to one vendor. Set LLM_PROVIDER (default: anthropic) and the
matching API key; the rest of the core talks to a thin LLMClient.complete() interface, so
adding or swapping a provider is a small change here and nowhere else.

Supported out of the box: anthropic, openai. Add another by extending _build()/complete().
"""
import os
import re
import json

MODEL = os.getenv("LLM_MODEL", "claude-haiku-4-5")
PROVIDER = os.getenv("LLM_PROVIDER", "anthropic").lower()


class LLMClient:
    """One method the whole core depends on: complete(system, user, max_tokens) -> text.

    The vendor SDK lives behind this wrapper, so the core is provider-agnostic.
    """

    def __init__(self, provider=None, model=None):
        self.provider = (provider or PROVIDER).lower()
        self.model = model or MODEL
        self._kind, self._impl = self._build()

    def _build(self):
        if self.provider == "anthropic":
            from anthropic import Anthropic
            key = os.getenv("ANTHROPIC_API_KEY")
            if not key:
                raise RuntimeError(_missing_key_msg("ANTHROPIC_API_KEY"))
            return "anthropic", Anthropic(api_key=key)
        if self.provider == "openai":
            from openai import OpenAI
            key = os.getenv("OPENAI_API_KEY")
            if not key:
                raise RuntimeError(_missing_key_msg("OPENAI_API_KEY"))
            return "openai", OpenAI(api_key=key)
        raise ValueError(
            f"Unknown LLM_PROVIDER '{self.provider}'. Supported: anthropic, openai. "
            "Add your own in core/llm.py."
        )

    def complete(self, system, user, max_tokens=2000):
        if self._kind == "anthropic":
            resp = self._impl.messages.create(
                model=self.model, max_tokens=max_tokens, system=system,
                messages=[{"role": "user", "content": user}],
            )
            return resp.content[0].text
        if self._kind == "openai":
            resp = self._impl.chat.completions.create(
                model=self.model, max_tokens=max_tokens,
                messages=[{"role": "system", "content": system},
                          {"role": "user", "content": user}],
            )
            return resp.choices[0].message.content
        raise RuntimeError(f"provider not wired: {self._kind}")


def _missing_key_msg(var):
    return (
        f"{var} not set. Copy .env.example to .env and add your key for live mode, "
        "or use the committed samples (no key needed)."
    )


def get_client(provider=None, model=None):
    """Return a provider-agnostic LLM client (raises a clear error if the key is missing)."""
    return LLMClient(provider=provider, model=model)


def extract_json(text):
    """Robustly pull the first complete JSON value out of an LLM reply.

    Handles markdown fences, prose before/after, and trailing 'extra data'.
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

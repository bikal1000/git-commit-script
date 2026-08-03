"""Optional AI-generated commit subject line via any OpenAI-compatible API.

Strictly opt-in: only invoked when the caller passes --ai. Never required
for core functionality, and falls back silently (with a warning) to the
rule-based suggestion on any failure.

Works with OpenAI itself and any OpenAI-compatible endpoint (Azure OpenAI,
Groq, Together, Ollama, vLLM, LM Studio, etc.) by pointing OPENAI_BASE_URL
at that endpoint.
"""

from __future__ import annotations

import os

DEFAULT_MODEL = "gpt-4o-mini"
MAX_DIFF_CHARS = 12000  # rough token-budget guard for the prompt

SYSTEM_PROMPT = (
    "You write git commit subject lines. Given a staged diff, respond with "
    "ONLY a single concise, imperative-mood commit subject line under 72 "
    "characters. No prefix, no quotes, no trailing period, no explanation."
)


class LLMError(RuntimeError):
    """Raised when the AI suggestion could not be produced."""


def suggest_subject_ai(diff_text: str) -> str:
    """Ask an OpenAI-compatible chat completions API for a commit subject.

    Raises LLMError on any failure so callers can fall back to the
    rule-based suggestion.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise LLMError("OPENAI_API_KEY is not set")

    base_url = os.environ.get("OPENAI_BASE_URL")
    model = os.environ.get("OPENAI_MODEL", DEFAULT_MODEL)

    try:
        import openai
    except ImportError as exc:
        raise LLMError(
            "the 'openai' package is not installed (pip install 'commit-lint[ai]')"
        ) from exc

    truncated = diff_text[:MAX_DIFF_CHARS]

    try:
        client = openai.OpenAI(api_key=api_key, base_url=base_url)
        response = client.chat.completions.create(
            model=model,
            max_tokens=64,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": truncated},
            ],
        )
        text = (response.choices[0].message.content or "").strip()
    except Exception as exc:  # any SDK/network failure should fall back to rule-based
        raise LLMError(f"OpenAI-compatible API call failed: {exc}") from exc

    if not text:
        raise LLMError("API returned an empty response")

    subject = text.strip().strip('"').splitlines()[0].strip()
    return subject[:72]

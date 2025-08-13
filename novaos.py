# novaos.py — safe model wrapper used by the dashboard
import os
from typing import Optional

# Optional: lightweight sanitization of prompts so logs don't leak tokens
def _redact(s: str) -> str:
    if not s:
        return s
    return s.replace(os.environ.get("OPENAI_API_KEY", ""), "[REDACTED]")

def _call_model(prompt: str) -> str:
    """
    Safe model call:
    - If OPENAI_API_KEY is missing, return a helpful message instead of crashing.
    - No 'proxies' or other unsupported kwargs.
    - Uses Chat Completions API compatible with openai==1.51.x.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "LLM disabled: set OPENAI_API_KEY in Render → Environment (then redeploy)."

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)  # no 'proxies' passed
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are NovaOS Build Commander. Be concise, step-by-step, and decisive."},
                {"role": "user", "content": _redact(prompt)}
            ],
            temperature=0.2,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        # Never crash the page—surface the error in the UI
        return f"LLM error: {e}"

def ask(*, agent: str, task: str, query: Optional[str], k: int = 5) -> str:
    """
    Thin wrapper used by the UI.
    - agent: selected agent name
    - task: what you want done
    - query: optional keyword for memory search (handled upstream)
    - k: number of memory chunks (handled upstream)
    """
    prompt = f"""Agent: {agent}
Task: {task}
Query: {query or "(none)"}
Grounded memory chunks (k={k}) are fetched upstream.
Respond decisively, step-by-step, using the memory provided."""
    return _call_model(prompt)

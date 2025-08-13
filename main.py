# novaos.py
import os
import uuid
from typing import List, Dict, Any

# ───────────────────────── Optional memory import ─────────────────────────────
def _memory_enabled() -> bool:
    return bool(os.environ.get("DATABASE_URL"))

try:
    if _memory_enabled():
        from agents._lib.context_pg import fetch_context as _fetch_context  # type: ignore
    else:
        _fetch_context = None
except Exception:
    _fetch_context = None

def _get_context(query: str, k: int) -> List[Dict[str, Any]]:
    if not query or not _fetch_context:
        return []
    try:
        return _fetch_context(query, k=k) or []
    except Exception as e:
        print(f"[novaos] context fetch error: {e}", flush=True)
        return []

# ─────────────────────────── LLM call (OpenAI v1) ─────────────────────────────
def _call_model(prompt: str) -> str:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        # Stub answer so UI keeps working without a key.
        return "(stub) Model disabled — set OPENAI_API_KEY to enable real answers.\n\n" + prompt[:600]

    from openai import OpenAI
    import httpx  # present in your env already

    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY")

    http_client = None
    if proxy:
        # Proper proxy wiring for OpenAI v1.x
        http_client = httpx.Client(proxies=proxy, timeout=60.0, follow_redirects=True)

    client = OpenAI(api_key=api_key, http_client=http_client)

    # Use the Responses API (modern path)
    rsp = client.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": (
                    "You are NovaOS Build Commander. Be concise, step-by-step, no fluff. "
                    "Use provided context; if context is insufficient, say so clearly."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    )
    return rsp.output_text

# ───────────────────────────── Public entrypoint ──────────────────────────────
def ask(agent: str, task: str, query: str | None = None, k: int = 6) -> Dict[str, Any]:
    """
    Memory-first ask:
    - Pulls K snippets from Postgres (if DATABASE_URL present)
    - Builds a prompt
    - Calls OpenAI (or stub if no key)
    - Returns answer + context used + trace_id
    """
    q = (query or task or "").strip()
    ctx = _get_context(q, k=k) if q else []
    # Build compact context block
    lines = []
    for i, s in enumerate(ctx[:k]):
        doc = s.get("doc_id", "")
        content = (s.get("content", "") or "").replace("\n", " ")
        preview = content[:800]
        lines.append(f"({i+1}) [{doc}] {preview}")
    context_block = "\n".join(lines) if lines else "None"

    prompt = (
        f"Agent: {agent}\n"
        f"Task: {task}\n\n"
        f"Context (top {min(k, len(ctx))}):\n{context_block}\n\n"
        "Instructions:\n"
        "- Use the context when relevant. If context is insufficient, say exactly what is missing.\n"
        "- Answer in crisp steps. No filler. No speculation.\n"
    )

    answer = _call_model(prompt)
    trace_id = f"run/{uuid.uuid4().hex[:12]}"
    return {
        "answer": answer,
        "context_used": [
            {"doc_id": s.get("doc_id", ""), "score": s.get("score", 0.0), "content": s.get("content", "")}
            for s in ctx
        ],
        "trace_id": trace_id,
    }

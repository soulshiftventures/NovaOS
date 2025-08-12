# novaos.py
import os
import uuid
from typing import List, Dict, Any

# ───────────────────────── Memory (optional) ─────────────────────────
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

# ───────────────────────── Model selection ───────────────────────────
def _candidate_models() -> List[str]:
    """
    Priority:
      1) OPENAI_MODEL (your explicit pick — e.g., a v5 name)
      2) OPENAI_MODEL_FALLBACKS (comma-separated)
      3) sane defaults (5-first, then 4-family)
    """
    picks = []
    env_pick = (os.environ.get("OPENAI_MODEL") or "").strip()
    if env_pick:
        picks.append(env_pick)

    env_fallbacks = (os.environ.get("OPENAI_MODEL_FALLBACKS") or "").strip()
    if env_fallbacks:
        picks.extend([m.strip() for m in env_fallbacks.split(",") if m.strip()])

    # Defaults — safe, common names. If your account has v5 models, put their exact IDs in OPENAI_MODEL.
    defaults = [
        "gpt-5o", "gpt-5o-mini",   # if available on your account
        "gpt-4.1", "gpt-4.1-mini",
        "gpt-4o", "gpt-4o-mini",
    ]
    for m in defaults:
        if m not in picks:
            picks.append(m)
    return picks

# ─────────────────────────── LLM call ────────────────────────────────
def _call_model_with(model: str, prompt: str, client) -> str:
    rsp = client.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": (
                    "You are NovaOS Build Commander. Be concise, step-by-step, no fluff. "
                    "Use provided context; if context is insufficient, say exactly what is missing."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    )
    return rsp.output_text

def _call_model(prompt: str) -> str:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        return "(stub) Model disabled — set OPENAI_API_KEY to enable real answers.\n\n" + prompt[:600]

    from openai import OpenAI
    import httpx

    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY")
    http_client = httpx.Client(proxies=proxy, timeout=60.0, follow_redirects=True) if proxy else None

    print("[novaos] building OpenAI client (http_client set:", bool(http_client), ")", flush=True)
    client = OpenAI(api_key=api_key, http_client=http_client)

    last_err = None
    for model in _candidate_models():
        try:
            print(f"[novaos] trying model: {model}", flush=True)
            return _call_model_with(model, prompt, client)
        except Exception as e:
            msg = str(e).lower()
            # keep going if it's a model/availability issue; bail on hard failures later
            if "model" in msg and ("not found" in msg or "does not exist" in msg or "unknown" in msg):
                last_err = e
                continue
            if "rate limit" in msg or "429" in msg:
                last_err = e
                continue
            # capture but still try next; worst case we return last error
            last_err = e
            continue

    return f"(error) unable to get a model response. last_error={last_err}"

# ───────────────────────── Public entrypoint ─────────────────────────
def ask(agent: str, task: str, query: str | None = None, k: int = 6) -> Dict[str, Any]:
    q = (query or task or "").strip()
    ctx = _get_context(q, k=k) if q else []

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

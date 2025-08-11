"""
NovaOS core brain — single entrypoint for all agent LLM calls.

What this does:
- Pulls top-K memory snippets from Postgres before any model call.
- Builds a structured prompt (vision/guardrails/context/task).
- Calls OpenAI if OPENAI_API_KEY is present; otherwise uses a safe stub so it never crashes.
- Writes an audit trail to Postgres (inputs, context used, and output).
- Returns {answer, context_used, trace_id} for downstream agents.

Usage from ANY agent/module:
    from novaos import ask
    result = ask(
        agent="NovaCoreAgent",
        task="Draft a 3-step launch checklist for the dashboard",
        query="ops/vision",   # optional; if omitted we use the task text
        k=6                    # number of memory snippets to load
    )
    print(result["answer"])
"""

from __future__ import annotations
import os
import json
import time
import datetime as dt
from typing import List, Dict, Any, Optional

# Memory API (DB-backed)
try:
    from agents._lib.context_pg import fetch_context, learn
except Exception as e:
    # Hard fail loudly once; callers still get a friendly error structure.
    raise RuntimeError(f"[novaos] Unable to import memory backend: {e}")

# --- OpenAI (optional) -------------------------------------------------------
_HAS_OPENAI = False
try:
    from openai import OpenAI  # openai>=1.x
    if os.getenv("OPENAI_API_KEY"):
        _HAS_OPENAI = True
except Exception:
    _HAS_OPENAI = False

# --- Helpers -----------------------------------------------------------------
def _now_iso() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def _safe_json(obj: Any) -> str:
    try:
        return json.dumps(obj, ensure_ascii=False)
    except Exception:
        return str(obj)

def _mk_trace_id(agent: str) -> str:
    ts = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    return f"runs/{agent.lower()}/{ts}"

def _summarize(snips: List[Dict[str, Any]], max_chars: int = 1200) -> str:
    """Concatenate snippets into a bounded block."""
    out = []
    used = 0
    for s in snips:
        chunk = s.get("content", "")
        if not chunk:
            continue
        # Light trim per snippet
        chunk = chunk.strip()
        if len(chunk) > 500:
            chunk = chunk[:500] + " ..."
        if used + len(chunk) + 1 > max_chars:
            break
        out.append(chunk)
        used += len(chunk) + 1
    return "\n\n".join(out)

# --- Prompt builder ----------------------------------------------------------
SYSTEM_GUARDRAILS = """You are NovaOS Build Commander.
- Be step-by-step, explicit, and TBI-friendly. No filler.
- Use best-practice defaults; avoid open-ended choices.
- Treat 'ops/vision' and 'ops/guardrails' as canonical if present.
- If unsure, explain the assumption and proceed.
"""

def _build_prompt(agent: str, task: str, memory_block: str) -> str:
    return f"""# ROLE
{SYSTEM_GUARDRAILS}
Agent: {agent}

# CONTEXT (from memory)
{memory_block or "[no relevant memory found]"}

# TASK
{task}

# OUTPUT RULES
- Give the answer directly.
- Use numbered steps if procedural.
- Keep it concise and executable.
"""

# --- Model caller ------------------------------------------------------------
def _call_model(prompt: str) -> str:
    """Call OpenAI if configured; else return a deterministic stub."""
    if _HAS_OPENAI:
        client = OpenAI()
        # gpt-4o-mini is cheap/fast; change model here centrally if needed.
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are a precise, direct operator."},
                      {"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return (resp.choices[0].message.content or "").strip()
    # Fallback: echo-style, still useful for dev and tests
    return (
        "MODEL_STUB: OpenAI not configured.\n"
        "I would answer based on the provided context and task.\n"
        "----\n"
        + prompt[:1800]
    )

# --- Public API --------------------------------------------------------------
def ask(agent: str, task: str, query: Optional[str] = None, k: int = 6) -> Dict[str, Any]:
    """
    Memory-first LLM call.
    Returns:
        {
          "answer": str,
          "context_used": [ {doc_id, score, preview}, ... ],
          "trace_id": str
        }
    """
    if not isinstance(agent, str) or not agent.strip():
        raise ValueError("agent is required")
    if not isinstance(task, str) or not task.strip():
        raise ValueError("task is required")

    q = (query or task).strip()
    # 1) Pull memory
    try:
        snippets = fetch_context(q, k=max(1, int(k)))
    except Exception as e:
        snippets = []
        # Persist the failure in memory for audit
        _safe_learn("ops/errors", f"[{_now_iso()}] fetch_context failed for '{q}': {e}", tags=["error","memory"])

    # 2) Build prompt
    mem_block = _summarize(snippets)
    prompt = _build_prompt(agent, task, mem_block)

    # 3) Call model (or stub)
    start = time.time()
    answer = _call_model(prompt)
    dur_ms = int((time.time() - start) * 1000)

    # 4) Persist audit (inputs, context, output)
    trace_id = _mk_trace_id(agent)
    try:
        ctx_preview = [
            {
                "doc_id": s.get("doc_id", ""),
                "score": float(s.get("score", 0.0)),
                "preview": (s.get("content", "")[:180] + "…") if s.get("content") else ""
            }
            for s in snippets
        ]
        _safe_learn(
            doc_id=f"{trace_id}/input",
            content=_safe_json({
                "ts": _now_iso(),
                "agent": agent,
                "task": task,
                "query": q,
                "k": k,
                "context_used": ctx_preview,
            }),
            tags=["trace","input"]
        )
        _safe_learn(
            doc_id=f"{trace_id}/output",
            content=_safe_json({
                "ts": _now_iso(),
                "agent": agent,
                "duration_ms": dur_ms,
                "answer": answer
            }),
            tags=["trace","output"]
        )
    except Exception as e:
        _safe_learn("ops/errors", f"[{_now_iso()}] audit persist failed for '{trace_id}': {e}", tags=["error","audit"])

    return {"answer": answer, "context_used": snippets, "trace_id": trace_id}

# --- Robust memory write -----------------------------------------------------
def _safe_learn(doc_id: str, content: str, tags: Optional[List[str]] = None) -> None:
    try:
        learn(doc_id, content, tags or [])
    except Exception as _e:
        # Last resort: print so Render logs capture it
        print(f"[novaos._safe_learn] failed doc_id={doc_id}: {_e}", flush=True)

# Optional: quick self-test when run directly
if __name__ == "__main__":
    print("[novaos] self-test starting…", flush=True)
    res = ask(agent="NovaCoreAgent", task="Summarize our current NovaOS vision in 3 bullets.", query="ops/vision", k=5)
    print("[novaos] answer:\n", res["answer"])
    print("[novaos] trace_id:", res["trace_id"])

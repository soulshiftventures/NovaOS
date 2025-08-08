# agents/_lib/telemetry.py
import os
import json
import time
import urllib.request
import urllib.error

# Memory service base URL. Uses env var if set, otherwise defaults to your Render memory service.
MEM_URL = os.getenv("NOVA_MEM_URL", "https://novaosmem.onrender.com").rstrip("/")

def _post_json(path: str, data: dict, timeout: int = 5) -> dict:
    url = f"{MEM_URL}{path}"
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8") or "{}"
        try:
            return json.loads(raw)
        except Exception:
            return {"ok": False, "raw": raw}

def emit(agent: str, type: str, topic: str, payload: dict) -> dict:
    """
    Send a telemetry event to the Memory service.
    Safe: prints an error and returns {'ok': False} if anything fails.
    """
    event = {
        "data": {
            "agent": agent,
            "type": type,
            "topic": topic,
            "payload": payload,
            "ts": time.time(),
        }
    }
    try:
        res = _post_json("/tools/memory.write", event)
        key = res.get("key", "?")
        print(f"[telemetry] wrote {agent}:{topic} -> {key}")
        return res
    except Exception as e:
        print(f"[telemetry] FAILED {agent}:{topic}: {e}")
        return {"ok": False, "error": str(e)}

# Optional helpers if you want them later:
def lifecycle(agent: str, status: str) -> dict:
    return emit(agent, "event", "lifecycle", {"status": status})

def heartbeat(agent: str) -> dict:
    return emit(agent, "event", "heartbeat", {"alive": True})

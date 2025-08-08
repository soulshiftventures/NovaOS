import os, sys, time, requests, json
from pathlib import Path
import runpy

AGENT_NAME = "TrendAnalyzer"
MCP_MEMORY_URL = os.getenv("MCP_MEMORY_URL")  # e.g. https://novaosmem.onrender.com

AGENT_DIR = Path(__file__).resolve().parent
AGENT_MAIN = AGENT_DIR / "main.py"

def mem_write(payload: dict):
    if not MCP_MEMORY_URL: return
    try:
        requests.post(f"{MCP_MEMORY_URL}/tools/memory.write", json={"data": payload}, timeout=5)
    except Exception:
        pass

def mem_search(q: str, limit: int = 20):
    if not MCP_MEMORY_URL: return []
    try:
        r = requests.post(f"{MCP_MEMORY_URL}/tools/memory.search",
                          json={"q": q, "limit": limit}, timeout=10)
        r.raise_for_status()
        return r.json().get("results", [])
    except Exception:
        return []

def main():
    os.chdir(AGENT_DIR)
    mem_write({"agent": AGENT_NAME, "type": "event", "topic": "lifecycle",
               "payload": {"status": "starting", "exec": str(AGENT_MAIN)}, "ts": time.time()})

    # If there's no agent logic yet, provide a safe default loop reading Perplexity artifacts
    if not AGENT_MAIN.exists():
        # simple heartbeat + recent artifact peek so we see activity
        recent = mem_search("PerplexityFetcher")
        mem_write({"agent": AGENT_NAME, "type": "state", "topic": "bootstrap",
                   "payload": {"recent_refs": len(recent)},"ts": time.time()})
        time.sleep(60)
        sys.exit(0)

    try:
        runpy.run_path(str(AGENT_MAIN), run_name="__main__")
        code = 0
    except SystemExit as e:
        code = int(e.code) if isinstance(e.code, int) else 1
    except Exception as e:
        print(f"[entrypoint:{AGENT_NAME}] Unhandled error: {e}", flush=True)
        code = 1

    mem_write({"agent": AGENT_NAME, "type": "event", "topic": "lifecycle",
               "payload": {"status": "exited", "code": code}, "ts": time.time()})
    sys.exit(code)

if __name__ == "__main__":
    main()

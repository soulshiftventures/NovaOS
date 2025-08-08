import os, sys, time, requests
from pathlib import Path
import runpy

AGENT_NAME = "PerplexityFetcher"
MCP_MEMORY_URL = os.getenv("MCP_MEMORY_URL")  # e.g. https://novaosmem.onrender.com

AGENT_DIR = Path(__file__).resolve().parent
AGENT_MAIN = AGENT_DIR / "main.py"

def mem_write(payload: dict):
    if not MCP_MEMORY_URL:
        return
    try:
        requests.post(f"{MCP_MEMORY_URL}/tools/memory.write", json={"data": payload}, timeout=5)
    except Exception:
        pass

def main():
    # Always run from the agent folder
    os.chdir(AGENT_DIR)

    mem_write({"agent": AGENT_NAME, "type": "event", "topic": "lifecycle",
               "payload": {"status": "starting", "exec": str(AGENT_MAIN)}, "ts": time.time()})

    print(f"[entrypoint] Executing {AGENT_MAIN}", flush=True)

    # Execute the agent's main.py as __main__ (no subprocess path issues)
    try:
        runpy.run_path(str(AGENT_MAIN), run_name="__main__")
        code = 0
    except SystemExit as e:
        code = int(e.code) if isinstance(e.code, int) else 1
    except Exception as e:
        print(f"[entrypoint] Unhandled error: {e}", flush=True)
        code = 1

    mem_write({"agent": AGENT_NAME, "type": "event", "topic": "lifecycle",
               "payload": {"status": "exited", "code": code}, "ts": time.time()})
    sys.exit(code)

if __name__ == "__main__":
    main()

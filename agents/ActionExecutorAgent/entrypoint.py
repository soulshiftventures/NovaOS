import os, sys, time, runpy, requests
from pathlib import Path
AGENT_NAME = "ActionExecutorAgent"
AGENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = AGENT_DIR.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
os.chdir(AGENT_DIR)

MCP_MEMORY_URL = os.getenv("MCP_MEMORY_URL")
def mem_write(p):
    if not MCP_MEMORY_URL: return
    try: requests.post(MCP_MEMORY_URL.rstrip('/') + "/tools/memory.write", json={"data": p}, timeout=5)
    except Exception: pass

mem_write({"agent": AGENT_NAME, "type":"event", "topic":"lifecycle", "payload":{"status":"starting"}, "ts": time.time()})
code = 0
try:
    runpy.run_path(str(AGENT_DIR / "main.py"), run_name="__main__")
except SystemExit as e:
    code = int(e.code) if isinstance(e.code, int) else 1
except Exception as e:
    print(f"[{AGENT_NAME} entrypoint] error: {e}", flush=True); code = 1
mem_write({"agent": AGENT_NAME, "type":"event", "topic":"lifecycle", "payload":{"status":"exited","code":code}, "ts": time.time()})
sys.exit(code)

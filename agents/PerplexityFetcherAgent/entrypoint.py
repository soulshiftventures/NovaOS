import os, sys, subprocess, requests, time
from pathlib import Path

AGENT_NAME = "PerplexityFetcher"
MCP_MEMORY_URL = os.getenv("MCP_MEMORY_URL")  # e.g. https://novaosmem.onrender.com

AGENT_DIR = Path(__file__).resolve().parent
AGENT_MAIN = str(AGENT_DIR / "main.py")

def mem_write(payload: dict):
    if not MCP_MEMORY_URL:
        return
    try:
        requests.post(f"{MCP_MEMORY_URL}/tools/memory.write", json={"data": payload}, timeout=5)
    except Exception:
        pass

def main():
    mem_write({"agent": AGENT_NAME, "type": "event", "topic": "lifecycle",
               "payload": {"status": "starting"}, "ts": time.time()})

    # Run the agent's own main.py with its directory as CWD
    proc = subprocess.Popen(
        [sys.executable, AGENT_MAIN],
        cwd=str(AGENT_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    for line in proc.stdout:
        line = line.rstrip("\n")
        sys.stdout.write(line + "\n")
        mem_write({"agent": AGENT_NAME, "type": "log", "topic": "stdout",
                   "payload": {"line": line}, "ts": time.time()})

    code = proc.wait()
    mem_write({"agent": AGENT_NAME, "type": "event", "topic": "lifecycle",
               "payload": {"status": "exited", "code": code}, "ts": time.time()})
    sys.exit(code)

if __name__ == "__main__":
    main()

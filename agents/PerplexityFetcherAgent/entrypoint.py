import os, sys, subprocess, requests, time

AGENT_NAME = "PerplexityFetcher"
MCP_MEMORY_URL = os.getenv("MCP_MEMORY_URL")  # e.g. https://novaosmem.onrender.com

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
    proc = subprocess.Popen(
        ["python3", "main.py"],
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

from fastapi import FastAPI
import os, requests, time

app = FastAPI()

MEM_URL = os.getenv("MCP_MEMORY_URL", "https://novaosmem.onrender.com").rstrip("/")

@app.get("/health")
def health():
    return {"ok": True, "service": "novaos-dashboard"}

@app.get("/ping-mem")
def ping_mem():
    try:
        requests.post(f"{MEM_URL}/tools/memory.write", json={"data":{
            "agent": "dashboard",
            "type": "event",
            "topic": "lifecycle",
            "payload": {"status": "ping"},
            "ts": time.time()
        }}, timeout=5)
        return {"ok": True, "posted_to": MEM_URL}
    except Exception as e:
        return {"ok": False, "error": str(e)}

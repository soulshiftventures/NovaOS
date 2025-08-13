import os, json, time
from fastapi import FastAPI
from urllib.request import Request, urlopen

app = FastAPI()

@app.get("/health")
def health():
    return {"ok": True, "service": "novaos-dashboard"}

def post_mem(payload: dict) -> dict:
    mem_url = os.environ.get("NOVA_MEM_URL", "https://novaosmem.onrender.com").rstrip("/")
    body = json.dumps({"data": payload}).encode("utf-8")
    req = Request(f"{mem_url}/tools/memory.write", data=body, headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=8) as resp:
        return json.loads(resp.read().decode("utf-8"))

@app.get("/ping-mem")
def ping_mem():
    payload = {
        "agent": "dashboard",
        "type": "event",
        "topic": "lifecycle",
        "payload": {"status": "ping"},
        "ts": time.time(),
    }
    mem_url = os.environ.get("NOVA_MEM_URL", "https://novaosmem.onrender.com")
    try:
        res = post_mem(payload)
        return {"ok": bool(res.get("ok")), "posted_to": mem_url, "key": res.get("key")}
    except Exception as e:
        return {"ok": False, "posted_to": mem_url, "error": str(e)}


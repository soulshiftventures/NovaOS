import os, time, threading, requests

MEM_URL = os.getenv("MCP_MEMORY_URL", "https://novaosmem.onrender.com").rstrip("/")

def post_event(agent: str, topic: str, payload: dict):
    try:
        requests.post(f"{MEM_URL}/tools/memory.write",
                      json={"data":{"agent":agent,"type":"event","topic":topic,"payload":payload,"ts":time.time()}},
                      timeout=5)
    except Exception:
        # Don't crash agents on telemetry failure
        pass

def start_heartbeat(agent: str, interval_sec: int = 60):
    def _hb():
        while True:
            post_event(agent, "heartbeat", {"alive": True})
            time.sleep(interval_sec)
    t = threading.Thread(target=_hb, daemon=True)
    t.start()

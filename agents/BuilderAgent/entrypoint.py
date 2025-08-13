#!/usr/bin/env python3
import os, sys, time, signal, json, urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path: sys.path.insert(0, ROOT)

NAME = "BuilderAgent"

telemetry = None
try:
    from agents._lib import telemetry as _telemetry
    telemetry = _telemetry
except Exception:
    telemetry = None

MEM_URL = os.environ.get("NOVA_MEM_URL", "https://novaosmem.onrender.com").rstrip("/")

def _post_mem(data: dict):
    try:
        req = urllib.request.Request(
            f"{MEM_URL}/tools/memory.write",
            data=json.dumps({"data": data}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            r.read()
    except Exception as e:
        print("memory.write failed:", e)

def emit(agent, type, topic, payload):
    if telemetry:
        try:
            if hasattr(telemetry, "emit"):
                return telemetry.emit(agent=agent, type=type, topic=topic, payload=payload)
            if hasattr(telemetry, "event"):
                return telemetry.event(agent=agent, type=type, topic=topic, payload=payload)
            if hasattr(telemetry, "write_event"):
                return telemetry.write_event(agent=agent, type=type, topic=topic, payload=payload)
            T = getattr(telemetry, "Telemetry", None)
            if T:
                t = T()
                for m in ("emit", "event", "write_event"):
                    if hasattr(t, m):
                        return getattr(t, m)(agent=agent, type=type, topic=topic, payload=payload)
        except Exception as e:
            print("telemetry call failed, falling back:", e)
    _post_mem({"agent": agent, "type": type, "topic": topic, "payload": payload, "ts": time.time()})

_running = True
def _stop(*_): 
    global _running; _running = False
signal.signal(signal.SIGTERM, _stop); signal.signal(signal.SIGINT, _stop)

emit(NAME, "event", "lifecycle", {"status": "started"})
try:
    while _running:
        emit(NAME, "event", "heartbeat", {"alive": True})
        time.sleep(60)
finally:
    emit(NAME, "event", "lifecycle", {"status": "stopped"})


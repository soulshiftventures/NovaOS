#!/usr/bin/env python3
import os, sys, time, signal
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path: sys.path.insert(0, ROOT)
try:
    from agents._lib import telemetry
except Exception:
    class _T:
        @staticmethod
        def emit(**kw): print("telemetry", kw)
    telemetry = _T()

NAME = "FoundationBuilder"
_running = True
def _stop(*_):
    global _running; _running = False
signal.signal(signal.SIGTERM, _stop); signal.signal(signal.SIGINT, _stop)

telemetry.emit(agent=NAME, type="event", topic="lifecycle", payload={"status":"started"})
while _running:
    telemetry.emit(agent=NAME, type="event", topic="heartbeat", payload={"alive": True})
    time.sleep(60)
telemetry.emit(agent=NAME, type="event", topic="lifecycle", payload={"status":"stopped"})


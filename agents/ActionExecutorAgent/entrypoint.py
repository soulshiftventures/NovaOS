#!/usr/bin/env python3
import time, threading, sys
from agents._lib import telemetry

NAME = "ActionExecutorAgent"

def _hb():
    while True:
        try:
            telemetry.heartbeat(agent=NAME)
        except Exception as e:
            print(f"[{NAME}] heartbeat error: {e}", flush=True)
        time.sleep(30)

def main():
    print("🛠️ [ActionExecutorAgent] booting...", flush=True)
    try:
        telemetry.lifecycle(agent=NAME, status="started")
        print("🛠️ [ActionExecutorAgent] lifecycle emitted", flush=True)
    except Exception as e:
        print(f"🛠️ [ActionExecutorAgent] lifecycle ERROR: {e}", flush=True)
    threading.Thread(target=_hb, daemon=True).start()
    print("🛠️ [ActionExecutorAgent] running", flush=True)
    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()


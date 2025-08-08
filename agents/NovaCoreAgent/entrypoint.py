#!/usr/bin/env python3
import time, threading
from agents._lib import telemetry

NAME = "NovaCoreAgent"

def _hb():
    while True:
        try:
            telemetry.heartbeat(agent=NAME)
        except Exception as e:
            print(f"[{NAME}] heartbeat error: {e}", flush=True)
        time.sleep(30)

def main():
    print("🧠 [NovaCoreAgent] booting v1", flush=True)
    try:
        telemetry.lifecycle(agent=NAME, status="started")
        print("🧠 [NovaCoreAgent] lifecycle emitted", flush=True)
    except Exception as e:
        print(f"🧠 [NovaCoreAgent] lifecycle ERROR: {e}", flush=True)
    threading.Thread(target=_hb, daemon=True).start()
    print("🧠 [NovaCoreAgent] running", flush=True)
    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()

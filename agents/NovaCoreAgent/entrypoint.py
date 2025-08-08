#!/usr/bin/env python3
import time, threading
from agents._lib import telemetry

NAME = "NovaCoreAgent"

def _hb():
    while True:
        try: telemetry.heartbeat(agent=NAME)
        except Exception as e: print(f"[{NAME}] heartbeat error: {e}")
        time.sleep(30)

def main():
    telemetry.lifecycle(agent=NAME, status="started")
    print("🧠 [NovaCoreAgent] Ready.")
    threading.Thread(target=_hb, daemon=True).start()
    while True: time.sleep(60)

if __name__ == "__main__":
    main()


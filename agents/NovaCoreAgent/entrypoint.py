#!/usr/bin/env python3
import time
import threading
from agents._lib import telemetry

NAME = "NovaCoreAgent"

def _heartbeat_loop():
    while True:
        try:
            telemetry.heartbeat(agent=NAME)
        except Exception as e:
            print(f"[{NAME}] heartbeat error: {e}")
        time.sleep(30)

def main():
    telemetry.lifecycle(agent=NAME, status="started")
    print("🧠 [NovaCoreAgent] Ready.")

    th = threading.Thread(target=_heartbeat_loop, daemon=True)
    th.start()

    # TODO: core orchestration loop goes here
    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()


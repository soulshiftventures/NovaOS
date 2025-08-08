#!/usr/bin/env python3
import time
import threading
from agents._lib import telemetry

NAME = "ActionExecutorAgent"

def _heartbeat_loop():
    while True:
        try:
            telemetry.heartbeat(agent=NAME)
        except Exception as e:
            print(f"[{NAME}] heartbeat error: {e}")
        time.sleep(30)

def main():
    telemetry.lifecycle(agent=NAME, status="started")
    print("🛠️ [ActionExecutorAgent] Standing by.")

    th = threading.Thread(target=_heartbeat_loop, daemon=True)
    th.start()

    # TODO: watch for actions and execute them
    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()


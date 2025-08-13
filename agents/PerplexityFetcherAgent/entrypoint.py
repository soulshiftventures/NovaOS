#!/usr/bin/env python3
import time
import threading
from agents._lib import telemetry

NAME = "PerplexityFetcherAgent"

def _heartbeat_loop():
    while True:
        try:
            telemetry.heartbeat(agent=NAME)
        except Exception as e:
            print(f"[{NAME}] heartbeat error: {e}")
        time.sleep(30)

def main():
    # lifecycle signal
    telemetry.lifecycle(agent=NAME, status="started")
    print("🧠 [PerplexityFetcherAgent] Listening for tasks...")

    # background heartbeats
    th = threading.Thread(target=_heartbeat_loop, daemon=True)
    th.start()

    # TODO: actual task listening/handling goes here
    # keep the process alive
    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()


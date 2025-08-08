#!/usr/bin/env python3
import os, time, signal

# uses the shared telemetry helper your other agents use
from agents._lib import telemetry

NAME = "RoadmapAgent"
running = True

def _stop(*_):
    global running
    running = False

signal.signal(signal.SIGTERM, _stop)

# lifecycle: started
telemetry.emit(agent=NAME, type="event", topic="lifecycle", payload={"status": "started"})

# simple keepalive loop; extend with real work later
while running:
    telemetry.emit(agent=NAME, type="event", topic="heartbeat", payload={"alive": True})
    time.sleep(60)

# lifecycle: stopped
telemetry.emit(agent=NAME, type="event", topic="lifecycle", payload={"status": "stopped"})


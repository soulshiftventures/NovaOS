#!/usr/bin/env python3
import os, subprocess, redis, time

r = redis.from_url(os.getenv("REDIS_URL"))
queue = os.getenv("REDIS_QUEUE", "novaos:queue")

def run():
    while True:
        item = r.blpop(queue, timeout=5)
        if not item:
            time.sleep(1)
            continue
        _, data = item
        cmd = data.decode()
        print(f"[Docker-Deployer] Running: {cmd}")
        # e.g., subprocess.run(["docker","compose","up","-d",cmd])
        subprocess.run(cmd.split())
        # no forwarding
        time.sleep(0.1)

if __name__ == "__main__":
    run()

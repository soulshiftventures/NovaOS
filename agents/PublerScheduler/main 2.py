#!/usr/bin/env python3
import os, redis, time

r = redis.from_url(os.getenv("REDIS_URL"))
queue = os.getenv("REDIS_QUEUE", "novaos:queue")

def run():
    while True:
        item = r.blpop(queue, timeout=5)
        if not item:
            continue
        _, data = item
        content = data.decode()
        print(f"[Publer-Scheduler] Received: {content}")
        # TODO: call Publer API to schedule a post
        time.sleep(0.1)

if __name__ == "__main__":
    run()

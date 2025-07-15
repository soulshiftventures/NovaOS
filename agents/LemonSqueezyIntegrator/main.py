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
        data = data.decode()
        print(f"[LemonSqueezy-Integrator] Received: {data}")
        # TODO: call LemonSqueezy API here
        # e.g., process sale, send download link
        # no forwarding needed unless chaining
        time.sleep(0.1)

if __name__ == "__main__":
    run()

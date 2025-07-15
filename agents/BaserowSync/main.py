#!/usr/bin/env python3
import os, redis, time

r = redis.from_url(os.getenv("REDIS_URL"))
queue = os.getenv("REDIS_QUEUE", "novaos:queue")

def run():
    while True:
        item = r.blpop(queue, timeout=5)
        if not item:
            # TODO: you might poll Baserow periodically here
            time.sleep(1)
            continue
        _, data = item
        row = data.decode()
        print(f"[Baserow-Sync] Processing row: {row}")
        # TODO: call Baserow API to upsert row data
        # Optionally publish back to queue:
        # r.rpush(queue, f\"Baserow-Sync done: {row}\")

if __name__ == "__main__":
    run()

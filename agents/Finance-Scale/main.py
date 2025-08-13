#!/usr/bin/env python3
import os, redis

r = redis.from_url(os.getenv("REDIS_URL"))
pub = os.getenv("REDIS_PUB", "novaos:tasks")

def run():
    for msg in r.listen():
        data = msg.get("data")
        if data:
            print(f"[{os.path.basename(__file__)}] Received: {data}")
            r.publish(pub, f"{os.path.basename(__file__)} done")

if __name__ == "__main__":
    run()

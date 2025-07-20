import os
import time
import redis

# Connect to Redis
redis_host = os.environ.get("REDIS_HOST", "redis")
r = redis.Redis(host=redis_host, port=6379, decode_responses=True)

def process_task(task: str) -> str:
    if task.startswith('Supplier options:'):
        return 'Headlines: ["Wear the Glow of Dusk", "Chase the Horizon", "Embark at Sunset"]'
    return None

def main_loop():
    while True:
        item = r.brpop("novaos:tasks", timeout=5)
        if item:
            _, task = item
            print(f"Received task: {task}")
            response = process_task(task)
            if response:
                r.lpush("novaos:tasks", response)
                print(f"Published response: {response}")
        time.sleep(1)

if __name__ == "__main__":
    main_loop()

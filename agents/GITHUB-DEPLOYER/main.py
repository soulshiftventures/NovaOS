import os, time, redis
r = redis.Redis(host=os.getenv('REDIS_HOST','redis'), port=6379, decode_responses=True)

def process_task(t):
    return f"${ROLE} handled: {t}"

while True:
    item = r.brpop("novaos:tasks", timeout=5)
    if item:
        _, task = item
        print(f"Received task: {task}")
        resp = process_task(task)
        r.lpush("novaos:tasks", resp)
        print(f"Published response: {resp}")
    time.sleep(1)

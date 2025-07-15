import redis
import json
import time

r = redis.Redis(host='redis', port=6379, decode_responses=True)

def handle_task(task):
    print("🛠 Handling task...")
    return {"status": "complete", "echo": task}

def handle_ping():
    print("📡 Received ping...")
    return {"status": "pong"}

while True:
    task_data = r.brpop("novaos:tasks", timeout=5)
    if task_data:
        _, raw_task = task_data
        try:
            task = json.loads(raw_task)
            task_type = task.get("type")

            if task_type == "task":
                result = handle_task(task)
            elif task_type == "ping":
                result = handle_ping()
            else:
                result = {"status": "error", "message": "Unknown task type"}

            r.lpush("novaos:results", json.dumps(result))
        except json.JSONDecodeError:
            print("❌ Failed to parse task:", raw_task)
    time.sleep(1)

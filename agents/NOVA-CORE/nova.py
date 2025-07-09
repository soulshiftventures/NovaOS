import os
import json
import time
import redis

def process_task(task_str):
    try:
        task = json.loads(task_str)
        task_type = task.get("type")

        if task_type == "ping":
            return {"type": "pong"}
        else:
            return {"error": f"Unknown task type: {task_type}"}
    except Exception as e:
        return {"error": f"Failed to process task: {str(e)}"}

def main():
    print("🌟 NOVA-CORE is online and ready.")

    redis_url = os.getenv("REDIS_URL", "redis://novaos_redis:6379/0")
    r = redis.Redis.from_url(redis_url)
    r.set("novaos_status", "running")

    print("✅ Connected to Redis and set status.")
    print("📡 Listening for tasks...")

    while True:
        try:
            _, task_str = r.blpop("novaos:tasks")
            task = json.loads(task_str)

            if task["type"] == "ping":
                print("👋 Pong received.")
                r.rpush("novaos:results", json.dumps({"status": "ok", "type": "pong"}))

            else:
                print(f"❓ Unknown task type: {task['type']}")

        except Exception as e:
            print(f"❌ Error processing task: {e}")

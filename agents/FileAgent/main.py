import os
import redis
import json
import datetime

# Redis setup
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
r = redis.from_url(redis_url)

queue = "novaos:commands"
agent_name = "FileAgent"

print(f"[{agent_name}] Listening on Redis queue '{queue}'...")

def handle_task(task):
    payload = task.get("payload", {})
    action = payload.get("action")

    if action == "create_file":
        filename = payload.get("filename", "default.txt")
        content = payload.get("content", "")
        try:
            with open(filename, "w") as f:
                f.write(content)
            print(f"[{agent_name}] File '{filename}' created.")
        except Exception as e:
            print(f"[{agent_name}] ERROR creating file: {e}")

# Main loop
pubsub = r.pubsub()
pubsub.subscribe(queue)

for message in pubsub.listen():
    if message["type"] != "message":
        continue
    try:
        data = json.loads(message["data"])
        if data.get("agent") == agent_name:
            print(f"[{agent_name}] Received task: {data}")
            handle_task(data)
    except Exception as e:
        print(f"[{agent_name}] ERROR processing message: {e}")


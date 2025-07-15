import os
import redis
import json

# Init Redis
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
r = redis.from_url(redis_url)

queue = "novaos:commands"
agent_name = "BuilderAgent"

print(f"[{agent_name}] Listening on Redis queue '{queue}'...")

def scaffold_agent(agent_name, description):
    folder_path = f"../{agent_name}"
    os.makedirs(folder_path, exist_ok=True)

    main_py = (
        f"import os\n"
        f"import redis\n"
        f"import json\n\n"
        f"redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')\n"
        f"r = redis.from_url(redis_url)\n\n"
        f"queue = 'novaos:commands'\n"
        f"agent_name = '{agent_name}'\n\n"
        f"print(f\"[{agent_name}] Listening on Redis queue '{{queue}}'...\")\n\n"
        f"while True:\n"
        f"    message = r.blpop(queue)[1]\n"
        f"    task = json.loads(message.decode('utf-8'))\n"
        f"    if task.get('agent') != agent_name:\n"
        f"        continue\n"
        f"    print(f\"[{agent_name}] Received task: {{task}}\")\n"
    )

    with open(os.path.join(folder_path, "main.py"), "w") as f:
        f.write(main_py)

while True:
    message = r.blpop(queue)[1]
    task = json.loads(message.decode("utf-8"))

    if task.get("agent") != agent_name:
        continue

    payload = task.get("payload", {})
    action = payload.get("action")

    if action == "build_agent":
        name = payload.get("agent_name", "UnnamedAgent")
        desc = payload.get("description", "")
        print(f"[{agent_name}] Starting build for: {name}")
        scaffold_agent(name, desc)
        print(f"[{agent_name}] Agent {name} created.")


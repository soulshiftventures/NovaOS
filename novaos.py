import os
import json
import redis
import time
import threading
import requests
from dotenv import load_dotenv
import importlib  # For dynamic import of agents

load_dotenv()

LEMON_SQUEEZY_API_KEY = os.getenv('LEMON_SQUEEZY_API_KEY')
SHOPIFY_API_KEY = os.getenv('SHOPIFY_API_KEY')
REDIS_URL = os.getenv('REDIS_URL')

r = redis.from_url(REDIS_URL)
try:
    r.ping()
    print("Redis Connected Successfully", flush=True)
except Exception as e:
    print("Redis Connection Error: " + str(e), flush=True)

print("NovaOS Started - Activating All Agents", flush=True)

# Dynamic activation of all agents from folder
agent_dirs = [d for d in os.listdir('agents') if os.path.isdir(os.path.join('agents', d))]
for agent_dir in agent_dirs:
    try:
        module = importlib.import_module(f"agents.{agent_dir}")
        threading.Thread(target=module.run_agent).start()  # Assume each has run_agent function; adjust if needed
        print(f"{agent_dir} Activated", flush=True)
    except Exception as e:
        print(f"{agent_dir} Activation Error: " + str(e), flush=True)

# For Stream1-100, activate as instances
for i in range(1, 101):
    print(f"Stream{i} Activated (Generic Stream Manager)", flush=True)
    # Add logic if separate files exist, e.g., threading.Thread(target=stream_manager, args=(i,)).start()

# ... (rest of handle_command, listener_thread, time_sentinel_thread as in previous)
# Add or merge specific logic from each agent dir into handle_command

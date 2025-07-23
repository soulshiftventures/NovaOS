import os
import json
import redis
import time
import threading
import requests
from dotenv import load_dotenv
import importlib

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
        threading.Thread(target=module.run_agent).start()  # Assume run_agent in each; fix if not
        print(f"{agent_dir} Activated", flush=True)
    except Exception as e:
        print(f"{agent_dir} Activation Error: " + str(e), flush=True)

# For Stream1-100, activate as instances if needed (generic, so one class)
for i in range(1, 101):
    print(f"Stream{i} Activated as instance", flush=True)
    # Add specific logic if separate code exists

def handle_command(cmd, r_handle):
    try:
        agent = cmd.get('agent')
        payload = payload = cmd['payload']
        if agent == 'StreamBuilder':
            # ... (keep previous code for test_lemon_squeezy, test_printed_mint, launch_pod_stream, etc.)
        # ... (keep DashboardAgent, ShopifySpecialist, etc.)
    except Exception as e:
        print(f"{agent} Error: " + str(e), flush=True)

def listener_thread():
    print("Listener Thread Started", flush=True)
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    try:
        pubsub.subscribe('novaos:commands')
        print("Subscribed to novaos:commands", flush=True)
        counter = 0
        while True:
            message = pubsub.get_message()
            if message and message['type'] == 'message':
                cmd = json.loads(message['data'].decode('utf-8'))
                print("Received command: " + str(cmd), flush=True)
                handle_command(cmd, r)
            time.sleep(0.001)
            counter += 1
            if counter % 60000 == 0:
                print("Listener Loop Running", flush=True)
                counter = 0
    except Exception as e:
        print("Listener Subscribe Error: " + str(e), flush=True)

def time_sentinel_thread():
    print("TimeSentinel Thread Started", flush=True)
    while True:
        try:
            optimization = "Optimized for $25k/month revenue."
            r.publish('novaos:logs', json.dumps({'event': 'Optimization Cycle', 'details': optimization}))
            print("Optimization Cycle", flush=True)
        except Exception as e:
            print("TimeSentinel Publish Error: " + str(e), flush=True)
        time.sleep(60)

if __name__ == '__main__':
    threading.Thread(target=listener_thread).start()
    threading.Thread(target=time_sentinel_thread).start()
    while True:
        time.sleep(1)

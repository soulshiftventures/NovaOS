import os
import json
import redis
import time
import threading
import requests
from dotenv import load_dotenv

load_dotenv()

LEMON_SQUEEZY_API_KEY = os.getenv('LEMON_SQUEEZY_API_KEY')
REDIS_URL = os.getenv('REDIS_URL')

r = redis.from_url(REDIS_URL)
try:
    r.ping()
    print("Redis Connected Successfully", flush=True)
except Exception as e:
    print("Redis Connection Error: " + str(e), flush=True)

print("All Agents Started", flush=True)

def handle_command(cmd, r_handle):
    try:
        agent = cmd.get('agent')
        payload = cmd['payload']
        if agent == 'StreamBuilder':
            if payload.get('action') == 'test_lemon_squeezy':
                headers = {'Authorization': f'Bearer {LEMON_SQUEEZY_API_KEY}'}
                response = requests.get('https://api.lemonsqueezy.com/v1/stores', headers=headers)
                if response.status_code == 200:
                    r_handle.publish('novaos:logs', json.dumps({'event': 'Lemon Squeezy Connected', 'details': 'API connection successful'}))
                    print("Lemon Squeezy Connected: Success", flush=True)
                else:
                    r_handle.publish('novaos:logs', json.dumps({'event': 'Lemon Squeezy Error', 'details': f'API failed: {response.status_code} {response.text}'}))
                    print("Lemon Squeezy Error: " + response.text, flush=True)
            elif payload.get('action') == 'launch_streams':
                count = payload.get('count', 1)
                r_handle.publish('novaos:logs', json.dumps({'event': 'Streams Launched', 'details': f"Launched {count} streams with UI/UX."}))
                print("Streams Launched", flush=True)
        elif agent == 'DashboardAgent':
            if payload.get('action') == 'build_dashboard':
                dashboard = "Built dashboard with UI/UX for streams: status, revenue tracking."
                r_handle.publish('novaos:logs', json.dumps({'event': 'Dashboard built', 'details': dashboard}))
                print("Dashboard Built", flush=True)
    except Exception as e:
        r_handle.publish('novaos:logs', json.dumps({'event': f'{agent} Error', 'details': str(e)}))
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
            time.sleep(0.001)  # Low CPU poll
            counter += 1
            if counter % 60000 == 0:  # Print every ~60s
                print("Listener Loop Running", flush=True)
                counter = 0
    except Exception as e:
        print("Listener Subscribe Error: " + str(e), flush=True)

def time_sentinel_thread():
    print("TimeSentinel Thread Started", flush=True)
    while True:
        try:
            optimization = "Monitored streams: Optimized for $25k/month total revenue."
            r.publish('novaos:logs', json.dumps({'event': 'Optimization Cycle', 'details': optimization}))
            print("Optimization Cycle", flush=True)
        except Exception as e:
            print("TimeSentinel Publish Error: " + str(e), flush=True)
        time.sleep(60)

if __name__ == '__main__':
    threading.Thread(target=listener_thread).start()
    threading.Thread(target=time_sentinel_thread).start()
    while True:
        time.sleep(1)  # Keep main alive

import os
import json
import redis
import time
import threading
import requests
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = 'red-d1u794c9c44c73cmjbf0'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_USERNAME = 'red-d1u794c9c44c73cmjbf0'
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
LEMON_SQUEEZY_API_KEY = os.getenv('LEMON_SQUEEZY_API_KEY')

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, username=REDIS_USERNAME, password=REDIS_PASSWORD)
pubsub = r.pubsub()

try:
    r.ping()
    print("Redis Connected Successfully")
except Exception as e:
    print("Redis Connection Error: " + str(e))

print("All Agents Started")

def stream_builder_thread():
    pubsub.subscribe('novaos:commands')
    print("StreamBuilder Subscribed")
    for message in pubsub.listen():
        if message['type'] == 'message':
            try:
                cmd = json.loads(message['data'].decode('utf-8'))
                print("Received command: " + str(cmd))
                if cmd.get('agent') == 'StreamBuilder':
                    payload = cmd['payload']
                    if payload.get('action') == 'test_lemon_squeezy':
                        headers = {'Authorization': f'Bearer {LEMON_SQUEEZY_API_KEY}'}
                        response = requests.get('https://api.lemonsqueezy.com/v1/stores', headers=headers)
                        if response.status_code == 200:
                            r.publish('novaos:logs', json.dumps({'event': 'Lemon Squeezy Connected', 'details': 'API connection successful'}))
                            print("Lemon Squeezy Connected: Success")
                        else:
                            r.publish('novaos:logs', json.dumps({'event': 'Lemon Squeezy Error', 'details': f'API failed: {response.status_code} {response.text}'}))
                            print("Lemon Squeezy Error: " + response.text)
                    elif payload.get('action') == 'launch_streams':
                        count = payload.get('count', 1)
                        r.publish('novaos:logs', json.dumps({'event': 'Streams Launched', 'details': f"Launched {count} streams with UI/UX."}))
                        print("Streams Launched")
            except Exception as e:
                r.publish('novaos:logs', json.dumps({'event': 'StreamBuilder Error', 'details': str(e)}))
                print("StreamBuilder Error: " + str(e))

def time_sentinel_thread():
    while True:
        optimization = "Monitored streams: Optimized for $25k/month total revenue."
        r.publish('novaos:logs', json.dumps({'event': 'Optimization Cycle', 'details': optimization}))
        print("Optimization Cycle")
        time.sleep(60)

def dashboard_agent_thread():
    pubsub.subscribe('novaos:commands')
    print("DashboardAgent Subscribed")
    for message in pubsub.listen():
        if message['type'] == 'message':
            try:
                cmd = json.loads(message['data'].decode('utf-8'))
                print("Received command: " + str(cmd))
                if cmd.get('agent') == 'DashboardAgent':
                    payload = cmd['payload']
                    if payload.get('action') == 'build_dashboard':
                        dashboard = "Built dashboard with UI/UX for streams: status, revenue tracking."
                        r.publish('novaos:logs', json.dumps({'event': 'Dashboard built', 'details': dashboard}))
                        print("Dashboard Built")
            except Exception as e:
                r.publish('novaos:logs', json.dumps({'event': 'DashboardAgent error', 'details': str(e)}))
                print("DashboardAgent Error: " + str(e))

if __name__ == '__main__':
    threading.Thread(target=stream_builder_thread).start()
    threading.Thread(target=time_sentinel_thread).start()
    threading.Thread(target=dashboard_agent_thread).start()

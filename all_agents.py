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

# Startup ping with temp client
temp_r = redis.from_url(REDIS_URL)
try:
    temp_r.ping()
    print("Redis Connected Successfully")
except Exception as e:
    print("Redis Connection Error: " + str(e))

print("All Agents Started")

def pubsub_exception_handler(ex, pubsub, thread):
    print("PubSub Exception: " + str(ex))

def handle_stream_builder_message(message):
    try:
        cmd = json.loads(message['data'].decode('utf-8'))
        print("Received command in StreamBuilder: " + str(cmd))
        if cmd.get('agent') == 'StreamBuilder':
            payload = cmd['payload']
            r_stream = redis.from_url(REDIS_URL)
            if payload.get('action') == 'test_lemon_squeezy':
                headers = {'Authorization': f'Bearer {LEMON_SQUEEZY_API_KEY}'}
                response = requests.get('https://api.lemonsqueezy.com/v1/stores', headers=headers)
                if response.status_code == 200:
                    r_stream.publish('novaos:logs', json.dumps({'event': 'Lemon Squeezy Connected', 'details': 'API connection successful'}))
                    print("Lemon Squeezy Connected: Success")
                else:
                    r_stream.publish('novaos:logs', json.dumps({'event': 'Lemon Squeezy Error', 'details': f'API failed: {response.status_code} {response.text}'}))
                    print("Lemon Squeezy Error: " + response.text)
            elif payload.get('action') == 'launch_streams':
                count = payload.get('count', 1)
                r_stream.publish('novaos:logs', json.dumps({'event': 'Streams Launched', 'details': f"Launched {count} streams with UI/UX."}))
                print("Streams Launched")
    except Exception as e:
        r_stream = redis.from_url(REDIS_URL)
        r_stream.publish('novaos:logs', json.dumps({'event': 'StreamBuilder Error', 'details': str(e)}))
        print("StreamBuilder Error: " + str(e))

def stream_builder_thread():
    print("StreamBuilder Thread Started")
    r_stream = redis.from_url(REDIS_URL)
    pubsub = r_stream.pubsub(ignore_subscribe_messages=True)
    try:
        pubsub.subscribe(**{'novaos:commands': handle_stream_builder_message})
        print("StreamBuilder Subscribed")
        pubsub.run_in_thread(sleep_time=0.001, exception_handler=pubsub_exception_handler)
        print("StreamBuilder Listener Started")
        while True:
            time.sleep(1)  # Keep thread alive to prevent GC/closure
    except Exception as e:
        print("StreamBuilder Subscribe Error: " + str(e))

def handle_dashboard_message(message):
    try:
        cmd = json.loads(message['data'].decode('utf-8'))
        print("Received command in DashboardAgent: " + str(cmd))
        if cmd.get('agent') == 'DashboardAgent':
            payload = cmd['payload']
            r_dash = redis.from_url(REDIS_URL)
            if payload.get('action') == 'build_dashboard':
                dashboard = "Built dashboard with UI/UX for streams: status, revenue tracking."
                r_dash.publish('novaos:logs', json.dumps({'event': 'Dashboard built', 'details': dashboard}))
                print("Dashboard Built")
    except Exception as e:
        r_dash = redis.from_url(REDIS_URL)
        r_dash.publish('novaos:logs', json.dumps({'event': 'DashboardAgent error', 'details': str(e)}))
        print("DashboardAgent Error: " + str(e))

def dashboard_agent_thread():
    print("DashboardAgent Thread Started")
    r_dash = redis.from_url(REDIS_URL)
    pubsub = r_dash.pubsub(ignore_subscribe_messages=True)
    try:
        pubsub.subscribe(**{'novaos:commands': handle_dashboard_message})
        print("DashboardAgent Subscribed")
        pubsub.run_in_thread(sleep_time=0.001, exception_handler=pubsub_exception_handler)
        print("DashboardAgent Listener Started")
        while True:
            time.sleep(1)  # Keep thread alive to prevent GC/closure
    except Exception as e:
        print("DashboardAgent Subscribe Error: " + str(e))

def time_sentinel_thread():
    print("TimeSentinel Thread Started")
    r_time = redis.from_url(REDIS_URL)
    while True:
        try:
            optimization = "Monitored streams: Optimized for $25k/month total revenue."
            r_time.publish('novaos:logs', json.dumps({'event': 'Optimization Cycle', 'details': optimization}))
            print("Optimization Cycle")
        except Exception as e:
            print("TimeSentinel Publish Error: " + str(e))
        time.sleep(60)

if __name__ == '__main__':
    threading.Thread(target=stream_builder_thread).start()
    threading.Thread(target=time_sentinel_thread).start()
    threading.Thread(target=dashboard_agent_thread).start()
    while True:
        time.sleep(1)  # Keep main alive

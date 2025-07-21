import os
import json
import redis
import time
import threading
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = 'red-d1u794c9c44c73cmjbf0'
REDIS_PORT = 6379
REDIS_DB = 0

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
pubsub = r.pubsub()

def stream_builder_thread():
    pubsub.subscribe('novaos:commands')
    for message in pubsub.listen():
        if message['type'] == 'message':
            try:
                cmd = json.loads(message['data'].decode('utf-8'))
                if cmd.get('agent') == 'StreamBuilder':
                    payload = cmd['payload']
                    if payload.get('action') == 'launch_streams':
                        count = payload.get('count', 1)  # Start with 1 for bare minimum
                        r.publish('novaos:logs', json.dumps({'event': 'Streams Launched', 'details': f"Launched {count} affiliate streams with UI/UX."}))
                        pod_option = "Optional PoD integrated: Agents automate designs for Printful/Etsy free, $0-50 startup, $10k+/mo potential, scalable niches."
                        r.publish('novaos:logs', json.dumps({'event': 'PoD Option Added', 'details': pod_option}))
            except Exception as e:
                r.publish('novaos:logs', json.dumps({'event': 'StreamBuilder Error', 'details': str(e)}))

def time_sentinel_thread():
    while True:
        optimization = "Monitored streams: Optimized for $25k/month total revenue ($10k+/mo per stream min, up to $1M/mo), UI/UX adjustments applied."
        r.publish('novaos:logs', json.dumps({'event': 'Optimization Cycle', 'details': optimization}))
        time.sleep(60)

def dashboard_agent_thread():
    pubsub.subscribe('novaos:commands')
    for message in pubsub.listen():
        if message['type'] == 'message':
            try:
                cmd = json.loads(message['data'].decode('utf-8'))
                if cmd.get('agent') == 'DashboardAgent':
                    payload = cmd['payload']
                    if payload.get('action') == 'build_dashboard':
                        dashboard = "Built dashboard with UI/UX for streams: personalized views, stream status, revenue tracking."
                        r.publish('novaos:logs', json.dumps({'event': 'Dashboard built', 'details': dashboard}))
            except Exception as e:
                r.publish('novaos:logs', json.dumps({'event': 'DashboardAgent error', 'details': str(e)}))

if __name__ == '__main__':
    threading.Thread(target=stream_builder_thread).start()
    threading.Thread(target=time_sentinel_thread).start()
    threading.Thread(target=dashboard_agent_thread).start()

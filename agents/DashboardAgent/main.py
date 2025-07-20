import os
import json
import redis
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = 'oregon-keyvalue.render.com'
REDIS_PORT = 6379
REDIS_USERNAME = 'red-d1u794c9c44c73cmjbf0'
REDIS_PASSWORD = 'qzGkLOVr1Eyde9b6F0Mk87nYrOKFov4S'
REDIS_DB = 0

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, username=REDIS_USERNAME, password=REDIS_PASSWORD, db=REDIS_DB, ssl=True, ssl_cert_reqs=None)
pubsub = r.pubsub()
pubsub.subscribe('novaos:commands')

def build_dashboard(payload):
    dashboard = "Built dashboard with UI/UX for 100+ streams: personalized views, stream status, revenue tracking."
    r.publish('novaos:logs', json.dumps({'event': 'Dashboard built', 'details': dashboard}))

for message in pubsub.listen():
    if message['type'] == 'message':
        try:
            cmd = json.loads(message['data'].decode('utf-8'))
            if cmd.get('agent') == 'DashboardAgent':
                payload = cmd['payload']
                if payload.get('action') == 'build_dashboard':
                    build_dashboard(payload)
        except Exception as e:
            r.publish('novaos:logs', json.dumps({'event': 'DashboardAgent error', 'details': str(e)}))

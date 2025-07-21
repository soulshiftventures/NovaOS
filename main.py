import os
import json
import redis
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = 'red-d1u794c9c44c73cmjbf0'
REDIS_PORT = 6379
REDIS_DB = 0

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
pubsub = r.pubsub()
pubsub.subscribe('novaos:commands')

for message in pubsub.listen():
    if message['type'] == 'message':
        try:
            cmd = json.loads(message['data'].decode('utf-8'))
            if cmd.get('agent') == 'GrokWatcherAgent':
                payload = cmd['payload']
                if payload.get('action') == 'watch_grok':
                    # Example action for GrokWatcherAgent - replace with actual logic if known
                    result = "Watched Grok updates: New features detected."
                    r.publish('novaos:logs', json.dumps({'event': 'Grok Watched', 'details': result}))
        except Exception as e:
            r.publish('novaos:logs', json.dumps({'event': 'GrokWatcherAgent Error', 'details': str(e)}))

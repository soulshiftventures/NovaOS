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
            if cmd.get('agent') == 'RoadmapAgent':
                payload = cmd['payload']
                if payload.get('action') == 'create_roadmap':
                    roadmap = "Created roadmap: Trend research, low-cost plan ($0-100 startup), setup (free tools/social), launch, scale to $10k+/mo with profits, monitor for $25k total by Aug 4th."
                    r.publish('novaos:logs', json.dumps({'event': 'Roadmap Created', 'details': roadmap}))
        except Exception as e:
            r.publish('novaos:logs', json.dumps({'event': 'RoadmapAgent Error', 'details': str(e)}))

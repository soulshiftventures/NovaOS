import os
import json
import redis
from dotenv import load_dotenv

load_dotenv()

r = redis.Redis(host='red-d1u794c9c44c73cmjbf0', port=6379, db=0)
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

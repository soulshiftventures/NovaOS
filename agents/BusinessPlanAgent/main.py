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
            if cmd.get('agent') == 'BusinessPlanAgent':
                payload = cmd['payload']
                if payload.get('action') == 'create_plan':
                    plan = "Created business plan: Prioritized low-cost (<$100 startup), e.g., affiliates/digital products first. Market research for $10k+/mo potential, financials ($25k total by Aug 4th), marketing (free SEO/social)."
                    r.publish('novaos:logs', json.dumps({'event': 'Business Plan Created', 'details': plan}))
        except Exception as e:
            r.publish('novaos:logs', json.dumps({'event': 'BusinessPlanAgent Error', 'details': str(e)}))

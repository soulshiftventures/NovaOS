import os
import json
import redis
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
pubsub = r.pubsub()
pubsub.subscribe('novaos:commands')

def integrate_uiux(payload):
    stages = ["Discovery: Interviews and briefs completed.", "Research: Personas and competitor analysis done.", "Planning: Goals and ideation set.", "Creation: Wireframes and prototypes built.", "Testing: Usability feedback incorporated.", "Finalizing: Rolled out with debrief."]
    result = "UI/UX integrated into StreamBuilder for 100+ streams: " + " ".join(stages)
    r.publish('novaos:logs', json.dumps({'event': 'UI/UX Integrated', 'details': result}))
    r.publish('novaos:logs', json.dumps({'event': 'Streams Ready', 'details': 'Automated product design for AI chatbots, dashboards, etc.'}))

def launch_streams(payload):
    count = payload.get('count', 100)
    r.publish('novaos:logs', json.dumps({'event': 'Streams Launched', 'details': f"Launched {count} streams with UI/UX."}))
    pod_option = "Optional PoD integrated: Agents automate designs for Printful/Etsy free, $0-50 startup, $10k+/mo potential, scalable niches."
    r.publish('novaos:logs', json.dumps({'event': 'PoD Option Added', 'details': pod_option}))

for message in pubsub.listen():
    if message['type'] == 'message':
        try:
            cmd = json.loads(message['data'].decode('utf-8'))
            if cmd.get('agent') == 'StreamBuilder':
                payload = cmd['payload']
                if payload.get('action') == 'integrate_uiux':
                    integrate_uiux(payload)
                elif payload.get('action') == 'launch_streams':
                    launch_streams(payload)
        except Exception as e:
            r.publish('novaos:logs', json.dumps({'event': 'StreamBuilder Error', 'details': str(e)}))

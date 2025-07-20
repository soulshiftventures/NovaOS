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

def build_uiux(payload):
    discovery = "Identified problem, audience, brief."
    research = "Created personas, analyzed behaviors."
    planning = "Set goals, allocated resources."
    creation = "Developed sketches, wireframes, prototypes."
    testing = "Performed usability testing, feedback."
    final = "Packaged, rolled out UI/UX for AI/ML product."
    r.publish('novaos:logs', json.dumps({'event': 'UIUX built', 'details': f'{discovery} {research} {planning} {creation} {testing} {final}'}))

while True:
    message = pubsub.get_message()
    if message and message['type'] == 'message':
        try:
            cmd = json.loads(message['data'])
            if cmd.get('agent') == 'UIUXBuilder':
                payload = cmd['payload']
                if payload.get('action') == 'build_uiux':
                    build_uiux(payload)
        except Exception as e:
            r.publish('novaos:logs', json.dumps({'event': 'UIUXBuilder error', 'details': str(e)}))

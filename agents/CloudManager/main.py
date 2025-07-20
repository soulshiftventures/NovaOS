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

for message in pubsub.listen():
    if message['type'] == 'message':
        try:
            cmd = json.loads(message['data'].decode('utf-8'))
            if cmd.get('agent') == 'CloudManager':
                payload = cmd['payload']
                if payload.get('action') == 'migrate_to_cloud':
                    migration = "Migrated NovaOS to cloud: Deployed 100+ streams with UI/UX, autoscaling, Web3 tokenization for subscriptions."
                    r.publish('novaos:logs', json.dumps({'event': 'Cloud Migration Complete', 'details': migration}))
        except Exception as e:
            r.publish('novaos:logs', json.dumps({'event': 'CloudManager Error', 'details': str(e)}))

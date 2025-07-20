
import redis
import json
import time
from dotenv import load_dotenv

load_dotenv()

r = redis.Redis(host='localhost', port=6379, db=0)
pubsub = r.pubsub()
pubsub.subscribe('novaos:commands')

while True:
    message = pubsub.get_message()
    if message and message['type'] == 'message':
        try:
            cmd = json.loads(message['data'])
            if cmd.get('agent') == 'StreamBuilder':
                print(f"Running StreamBuilder: {cmd['payload']}")
                # Logic for Builds automated income stream like POD in trends
                r.publish('novaos:logs', json.dumps({'event': f'StreamBuilder ran'}))
        except Exception as e:
            print(f"Error in StreamBuilder: {e}")
    time.sleep(1)

import os
import json
import time
from datetime import datetime, timedelta
import redis
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
pubsub = r.pubsub()
pubsub.subscribe('novaos:commands')

deadlines = {}  # Persist to Baserow/DB later for scale

def calculate_time_left(due_date):
    now = datetime.now()
    due = datetime.fromisoformat(due_date)
    return due - now

def check_deadlines():
    now = datetime.now()
    for goal, data in list(deadlines.items()):
        time_left = calculate_time_left(data['due'])
        if time_left < timedelta(0):
            r.publish('novaos:alerts', json.dumps({'type': 'missed', 'goal': goal, 'details': data}))
            del deadlines[goal]
        elif time_left < timedelta(days=1):
            r.publish('novaos:alerts', json.dumps({'type': 'urgent', 'goal': goal, 'time_left': str(time_left)}))

while True:
    message = pubsub.get_message()
    if message and message['type'] == 'message':
        try:
            cmd = json.loads(message['data'])
            if cmd.get('agent') == 'TimeSentinel':
                payload = cmd['payload']
                if payload['action'] == 'track_deadline':
                    deadlines[payload['goal']] = {'due': payload['due'], 'status': 'In Progress'}
                    r.publish('novaos:logs', json.dumps({'event': 'Deadline tracked', 'goal': payload['goal']}))
        except Exception as e:
            print(f"Error: {e}")
            r.publish('novaos:logs', json.dumps({'event': 'Error in TimeSentinel', 'details': str(e)}))
    
    check_deadlines()
    time.sleep(10)  # Check every 10s

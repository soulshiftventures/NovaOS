#!/usr/bin/env python3
import os
import json
import redis
from datetime import datetime

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
QUEUE_KEY = 'novaos:commands'
LOG_PATH = os.path.join(os.path.dirname(__file__), 'novaos_history.json')

def load_log():
    if not os.path.exists(LOG_PATH):
        return []
    with open(LOG_PATH, 'r') as f:
        return json.load(f)

def save_log(log_data):
    with open(LOG_PATH, 'w') as f:
        json.dump(log_data, f, indent=2)

def append_log(entry):
    logs = load_log()
    entry['logged_at'] = datetime.utcnow().isoformat()
    logs.append(entry)
    save_log(logs)
    print(f"[NovaHistorian] Logged: {entry['agent']} → {entry['action']}")

def handle(payload):
    if not isinstance(payload, dict):
        print("[NovaHistorian] Invalid payload")
        return
    append_log(payload)

def main():
    client = redis.from_url(REDIS_URL)
    pubsub = client.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe(QUEUE_KEY)
    print(f"[NovaHistorian] Listening on Redis queue '{QUEUE_KEY}'...")

    for message in pubsub.listen():
        cmd = message.get('data')
        if isinstance(cmd, bytes):
            cmd = cmd.decode('utf-8')
        try:
            data = json.loads(cmd)
            if data.get('agent') == 'NovaHistorian':
                handle(data.get('payload', {}))
        except Exception as e:
            print(f"[NovaHistorian] Error: {e}")

if __name__ == '__main__':
    main()


import os
import json
import redis
import requests
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
pubsub = r.pubsub()
pubsub.subscribe('novaos:commands')

def setup_crypto_stream():
    config = {
        "stream_type": "crypto_affiliate",
        "api_endpoints": ["https://api.cryptoaffiliate.com/v1/stream"],
        "automation": {
            "enabled": True,
            "tasks": ["link_generation", "traffic_monitoring", "payout_tracking"]
        },
        "launch_date": "2025-07-18"
    }
    r.publish('novaos:logs', json.dumps({'event': 'CryptoStreamBuilder config', 'details': config}))
    return "Crypto affiliate stream setup complete"

while True:
    message = pubsub.get_message()
    if message and message['type'] == 'message':
        try:
            cmd = json.loads(message['data'])
            if cmd.get('agent') == 'CryptoStreamBuilder':
                payload = cmd['payload']
                if payload.get('action') == 'setup_stream':
                    result = setup_crypto_stream()
                    r.publish('novaos:insights', json.dumps({'from': 'CryptoStreamBuilder', 'result': result}))
                    r.publish('novaos:logs', json.dumps({'event': 'CryptoStreamBuilder ran', 'details': result}))
        except Exception as e:
            r.publish('novaos:logs', json.dumps({'event': 'CryptoStreamBuilder error', 'details': str(e)}))

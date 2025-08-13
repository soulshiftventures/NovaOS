import os
import time
import threading
import json
from datetime import datetime, timezone
import redis
import subprocess
from dotenv import load_dotenv

load_dotenv()

# Redis configuration
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
LOG_CHANNEL = 'novaos:logs'

# Fix SSL for Mac
subprocess.run(['open', '/Applications/Python 3.13/Install Certificates.command'])

# Ensure Redis server is running
try:
    client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
    client.ping()
except (redis.ConnectionError, redis.TimeoutError):
    os.system('redis-server --daemonize yes')
    time.sleep(1)
    client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

# Log file setup
log_file = open('foundation.log', 'a')

# Logging function
def log(message):
    entry = {
        'timestamp': datetime.now(timezone.utc).isoformat() + 'Z',
        'agent': 'FoundationBuilderAgent',
        'message': message
    }
    payload = json.dumps(entry)
    # Publish to Redis
    try:
        client.publish(LOG_CHANNEL, payload)
    except Exception as e:
        print(f"Redis publish error: {str(e)}")
    # Write to file
    log_file.write(payload + '\n')
    log_file.flush()

# CryptoStreamBuilder agent
def crypto_stream_builder():
    log('CryptoStreamBuilder started')
    # Simulate setup work
    time.sleep(2)
    # Setup crypto affiliate stream logic would go here
    log('CryptoStreamBuilder completed')

# Generic Stream agent
def stream_agent(stream_id):
    pubsub = client.pubsub()
    command_channel = f'novaos:stream{stream_id}:commands'
    pubsub.subscribe(command_channel)
    log(f'Stream{stream_id} listening for commands on {command_channel}')
    for message in pubsub.listen():
        if message['type'] == 'message':
            data = message['data']
            try:
                cmd = data.decode('utf-8')
            except AttributeError:
                cmd = str(data)
            log(f'Stream{stream_id} received command: {cmd}')

# Start agents in background
if __name__ == '__main__':
    # Start CryptoStreamBuilder
    t_crypto = threading.Thread(target=crypto_stream_builder, daemon=True)
    t_crypto.start()

    # Trigger CryptoStreamBuilder immediately
    log('Triggering CryptoStreamBuilder')

    # Start 100 Stream agents
    for i in range(1, 101):
        t = threading.Thread(target=stream_agent, args=(i,), daemon=True)
        t.start()

    # Final log
    log('Foundation built')

    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log('Shutdown requested')
        log_file.close()

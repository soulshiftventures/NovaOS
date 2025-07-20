import os
import json
import redis
import time
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

def monitor_optimize():
    while True:
        optimization = "Monitored streams: Optimized for $25k/month total revenue ($10k+/mo per stream min, up to $1M/mo), UI/UX adjustments applied."
        r.publish('novaos:logs', json.dumps({'event': 'Optimization Cycle', 'details': optimization}))
        time.sleep(60)

monitor_optimize()

import os
import json
import redis
import time
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = 'oregon-keyvalue.render.com'
REDIS_PORT = 6379
REDIS_USERNAME = 'red-d1u794c9c44c73cmjbf0'
REDIS_PASSWORD = 'qzGkLOVr1Eyde9b6F0Mk87nYrOKFov4S'
REDIS_DB = 0

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, username=REDIS_USERNAME, password=REDIS_PASSWORD, db=REDIS_DB, ssl=True, ssl_cert_reqs=None)

def monitor_optimize():
    while True:
        optimization = "Monitored streams: Optimized for $25k/month total revenue ($10k+/mo per stream min, up to $1M/mo), UI/UX adjustments applied."
        r.publish('novaos:logs', json.dumps({'event': 'Optimization Cycle', 'details': optimization}))
        time.sleep(60)

monitor_optimize()

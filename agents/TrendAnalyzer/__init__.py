import redis
import json
import time
import os

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
r = redis.from_url(redis_url)

def analyze_trends():
    print("[TrendAnalyzer] Starting...")
    while True:
        try:
            data = r.lpop("novaos:results")
            if data:
                trend_data = json.loads(data)
                print("[TrendAnalyzer] Processing trend data:", trend_data)
                # Perform analysis or classification here
                summary = {
                    "summary": f"Trend count: {len(trend_data.get('trends', []))}",
                    "top_trend": trend_data.get('trends', [])[0] if trend_data.get('trends') else "None"
                }
                r.rpush("novaos:logs", json.dumps({"agent": "TrendAnalyzer", "result": summary}))
            else:
                time.sleep(5)
        except Exception as e:
            print("[TrendAnalyzer] Error:", str(e))
            time.sleep(5)


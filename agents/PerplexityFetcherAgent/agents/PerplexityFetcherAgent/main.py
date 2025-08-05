import os
import json
import time
import redis
import requests
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv('REDIS_URL')
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')

r = redis.from_url(REDIS_URL, decode_responses=True)

HEADERS = {
    "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
    "Content-Type": "application/json",
}

API_URL = "https://api.perplexity.ai/chat/completions"

def query_perplexity(prompt):
    payload = {
        "model": "sonar-pro",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 512,
    }
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data.get("choices")[0].get("message").get("content")
    else:
        return f"Error: {response.status_code} {response.text}"

def run():
    print("🧠 [PerplexityFetcherAgent] Listening for tasks...")
    while True:
        try:
            task_json = r.blpop("novaos:queue", timeout=5)
            if task_json:
                _, task_str = task_json
                task = json.loads(task_str)
                if task.get("type") == "perplexity_query" and "query" in task:
                    query = task["query"]
                    print(f"🔎 Received query: {query}")
                    answer = query_perplexity(query)
                    print(f"✅ Got answer: {answer}")
                    log_entry = json.dumps({
                        "timestamp": time.time(),
                        "query": query,
                        "answer": answer
                    })
                    r.lpush("novaos:logs", log_entry)
                else:
                    print(f"⚠️ Unsupported task or missing query: {task}")
            else:
                time.sleep(1)
        except Exception as e:
            print(f"❌ Exception in PerplexityFetcherAgent loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run()

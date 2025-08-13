import os, time, redis
r = redis.Redis(host=os.getenv('REDIS_HOST','redis'), port=6379, decode_responses=True)

def process_task(t):
    if t.startswith("Compliance:"):
        return 'Experience plan: ["Onboard flow","Feedback loop"]'
    if t.startswith("Experience plan:"):
        return 'Research summary: ["Market size data","Top competitors"]'
    if t.startswith("Research summary:"):
        return 'Clarity check: ✅ aligned with mission'
    if t.startswith("Clarity check:"):
        return 'Staff update: \"All clear, proceeding to launch\"'
    if t.startswith("Staff update:"):
        return 'Energy status: ✅ optimal'
    return None

while True:
    item = r.brpop("novaos:tasks", timeout=5)
    if item:
        _, task = item
        print(f"Received task: {task}")
        resp = process_task(task)
        if resp:
            r.lpush("novaos:tasks", resp)
            print(f"Published response: {resp}")
    time.sleep(1)

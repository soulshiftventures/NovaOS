import time
from agents._lib.memory import mem_search, enqueue_task, log_event

AGENT = "NovaCore"

def loop():
    log_event(AGENT, "lifecycle", {"status": "starting"})
    seen = set()

    while True:
        # Look for fresh artifacts from PerplexityFetcher
        artifacts = mem_search('"agent":"PerplexityFetcher","type":"artifact"', limit=30)
        created = 0
        for rec in artifacts:
            key = rec.get("key")
            if not key or key in seen: 
                continue
            seen.add(key)

            # Turn artifacts into executable tasks (placeholder: publish/store)
            enqueue_task(
                task_type="publish_artifact",
                payload={"source_key": key, "artifact": rec.get("data")},
                assigned_to="Executor",
                created_by=AGENT
            )
            created += 1

        if created:
            log_event(AGENT, "planner", {"created_tasks": created})

        # Heartbeat every 30s
        if int(time.time()) % 30 == 0:
            log_event(AGENT, "heartbeat", {"alive": True})

        time.sleep(5)

if __name__ == "__main__":
    loop()

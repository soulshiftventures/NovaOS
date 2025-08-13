import time, json
from agents._lib.memory import find_pending_tasks, claim_task, complete_task, log_event

AGENT = "Executor"

def handle_publish_artifact(task):
    src = task.get("payload", {}).get("source_key")
    artifact = task.get("payload", {}).get("artifact", {})
    # Placeholder "execution": just mirror it back as a result for now
    result = {"status":"published", "source_key": src, "summary": artifact.get("payload", {})}
    return result

HANDLERS = {
    "publish_artifact": handle_publish_artifact
}

def loop():
    log_event(AGENT, "lifecycle", {"status": "starting"})
    while True:
        # Look for work assigned to Executor
        tasks = find_pending_tasks(for_role="Executor", limit=20)
        for rec in tasks:
            key = rec.get("key")
            data = rec.get("data", {})
            task_type = data.get("task_type")
            claimed = claim_task(key, claimer=AGENT)
            if not claimed:
                continue  # someone else got it

            handler = HANDLERS.get(task_type)
            if not handler:
                complete_task(key, {"status":"skipped","reason":"no_handler"})
                continue

            try:
                result = handler(claimed)
                complete_task(key, result)
                log_event(AGENT, "exec", {"task_key": key, "task_type": task_type, "result": result})
            except Exception as e:
                complete_task(key, {"status":"error","error":str(e)})
                log_event(AGENT, "error", {"task_key": key, "err": str(e)})

        # steady cadence
        time.sleep(5)

if __name__ == "__main__":
    loop()
